#
#  cmd.py
#
#  Copyright (c)2023 Shane Ambler <Develop@ShaneWare.biz>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


import argparse
import boto3
from os.path import join, exists, expanduser
from pprint import pp
import signal
import subprocess as sp
import sys

from . import CLIOptions
from .__version__ import __version__ as vers
from .service.aws_ec2 import States

Opts = CLIOptions()
Opts.load()

NAMELEN = 24


def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)


def list_instances(ki):
    for idx in sorted(ki):
        kiip = ''
        if ki[idx]['state'] == States.RUNNING:
            kiip = ki[idx]['ip']
            if len(ki[idx]['ipv6']):
                for ip6 in ki[idx]['ipv6']:
                    kiip += f' - {ip6}'
        print(f'''{idx: 4d}: {ki[idx]['name'].ljust(NAMELEN, ' ')}'''
                f''' - {ki[idx]['id']} - {ki[idx]['st_name']} {kiip}''')


def main():
    ec2 = boto3.client('ec2')
    known_instances = {}
    run_count = 0

    parser = argparse.ArgumentParser(description='''Sawsc. Basic EC2 operations.''')
    parser.add_argument('--version', action='version', version='%(prog)s v'+vers)
    parser.add_argument('--debug', help='output debug info', action='store_true')
    parser.add_argument('-l', '--list', help='list all instances', action='store_true')
    parser.add_argument('-r', '--run', help='start an instance', action='store_true')
    parser.add_argument('-f', '--force', help='force reboot an instance', action='store_true')
    parser.add_argument('-s', '--ssh', help='ssh into an instance', action='store_true')
    parser.add_argument('-c', '--change', help='chnage instance type', action='store_true')
    parser.add_argument('-k', '--key', help='ssh key file', type=str, default='')
    parser.add_argument('ids', metavar='Id', type=str, nargs='*', help='Instance Id/s to start')
    args = parser.parse_args()

    if len(args.ids):
        print('Starting:')
        for i in args.ids:
            print(i)
        ec2.start_instances(InstanceIds=args.ids)
        return

    response = ec2.describe_instances()
    for r in response['Reservations']:
        for i in r['Instances']:
            # if i['State']['Code'] > 255: # clear top byte
            k_idx = len(known_instances) + 1
            known_instances[k_idx] = {  'state': i['State']['Code'],
                                        'st_name': i['State']['Name'],
                                        'id': i['InstanceId'],
                                        'type': i['InstanceType'],
                                        'name': '',
                                        'dnsname': '',
                                        'ip': '',
                                        'ipv6': [],}
            if 'Tags' in i:
                for t in i['Tags']:
                    if 'Key' in t and t['Key'] == 'Name':
                        known_instances[k_idx]['name'] = t['Value']

            if i['State']['Code'] == States.RUNNING:
                run_count += 1
                for ni in i['NetworkInterfaces']:
                    #pp(ni['Ipv6Addresses'])
                    for i6 in ni['Ipv6Addresses']:
                        known_instances[k_idx]['ipv6'] += [i6['Ipv6Address']]
                known_instances[k_idx]['dnsname'] = i['PublicDnsName']
                if 'PublicIpAddress' in i:
                    known_instances[k_idx]['ip'] = i['PublicIpAddress']

    if len(known_instances) < 1:
        print('No known ec2 instances.')
        return

    if args.list or not any(vars(args).values()):
        list_instances(known_instances)
        return

    # do I want to renumber this list?
    running_instances = {i: known_instances[i] for i in known_instances if known_instances[i]['state'] == States.RUNNING}

    if args.run:
        # only list stopped instances that we can start now
        # do I want to renumber this list?
        stopd_instances = {i: known_instances[i] for i in known_instances if known_instances[i]['state'] == States.STOPPED}
        list_instances(stopd_instances)
        try:
            choice = int(input('Start: '))
        except:
            choice = 0
        if choice > 0 and choice in stopd_instances:
            if stopd_instances[choice]['state'] == States.RUNNING:
                print(f'''{stopd_instances[choice]['name']} already running.''')
                exit(2)
            if stopd_instances[choice]['state'] == States.STOPPED:
                print(f'''Starting {stopd_instances[choice]['name']}''')
            else:
                print(f'''Unable to start {stopd_instances[choice]['name']} while {stopd_instances[choice]['st_name']}''')
                exit(2)
            try:
                ec2.start_instances(InstanceIds=[stopd_instances[choice]['id']])
            except Exception as e:
                print(e)
        return

    if args.force:
        if run_count < 1:
            print('No running instances.')
            exit(3)
        list_instances(running_instances)
        try:
            choice = int(input('Reboot: '))
        except:
            choice = 0
        if choice > 0 and choice in running_instances:
            ec2.reboot_instances(InstanceIds=[stopd_instances[choice]['id']])
        return

    if args.change:
        for idx in sorted(known_instances):
            c_state = ''
            if known_instances[idx]['state'] != States.STOPPED:
                c_state = f''' - {known_instances[idx]['st_name']}'''
            print(f'''{idx: 4d}: {known_instances[idx]['name'].ljust(NAMELEN, ' ')} - {known_instances[idx]['type']} {c_state}''')
        try:
            choice = int(input('Change: '))
        except:
            print()
            exit(4)

        for i in range(len(instance_types)):
            print(f'''{i: 4d}: {instance_types[i][0].ljust(13, ' ')} - {instance_types[i][1]}''')

        try:
            n_type = int(input(f'''Change {known_instances[choice]['name']} to: '''))
        except:
            print()
            exit(4)

        try:
            print(f'''Changing {known_instances[choice]['name']} to {instance_types[n_type][0]}''')
            ec2.modify_instance_attribute(
                            InstanceId=known_instances[choice]['id'],
                            InstanceType={'Value': instance_types[n_type][0]},
                            )
        except Exception as e:
            print(e)
            exit(4)

        return

    if args.ssh:
        if run_count < 1:
            print('No running instances.')
            exit(5)
        list_instances(running_instances)
        try:
            choice = int(input('ssh to: '))
        except:
            choice = 0
        if choice > 0 and choice in running_instances:
            if running_instances[choice]['state'] == States.RUNNING:
                print(f'''Connecting to {running_instances[choice]['name']}...''')
            else:
                print(f'''{running_instances[choice]['name']} not running.''')
                exit(5)
            try:
                if args.key:
                    keyfile = args.key
                else:
                    if running_instances[choice]['id'] in Opts.known_keys:
                        keyfile = Opts.known_keys[running_instances[choice]['id']]
                    else:
                        keyfile = '~/.ssh/aws_bb_sydney'
                cmd = ''
                if Opts.run_tmux:
                    cmd = 'tmux'
                if len(running_instances[choice]['ipv6']):
                    sh_args = ['ssh', '-6', '-t',
                                '-i', keyfile,
                                '-o ', 'IdentitiesOnly=yes',
                                'ec2-user@'+running_instances[choice]['ipv6'][0],
                                cmd]
                    if args.debug:
                        sh_args.insert(1, '-vvv')
                elif 'dnsname' in running_instances[choice]:
                    sh_args = ['ssh', '-t',
                                '-i', keyfile,
                                '-o ', 'IdentitiesOnly=yes',
                                'ec2-user@'+running_instances[choice]['dnsname'],
                                cmd]
                #pp(sargs)
                sp.call(' '.join(sh_args), shell=True)
            except Exception as e:
                print(f'nope: {e}')
        return


if __name__ == '__main__':
    main()

