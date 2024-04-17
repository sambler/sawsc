#
#  aws_ec2.py
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

import boto3
import subprocess as sp
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.tooltip import ToolTip

from . import ListBase

Opts = None # set from gui when making ListFrame
PADDING = 2

class States:
    # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html
    PENDING = 0
    RUNNING = 16
    SHUTTING_DOWN = 32
    TERMINATED = 48
    STOPPING = 64
    STOPPED = 80

# types lists - valid aws type to use is [0] from split by space
# only a personal selection here
TYPE_CHOICES = {
    'arm': [
        'c7g.medium - 1cpu arm 2G',
        'm7g.medium - 1cpu arm 4G',
        'r7g.medium - 1cpu arm 8G',

        'c7g.large - 2cpu arm 4G',
        'm7g.large - 2cpu arm 8G',
        'r7g.large - 2cpu arm 16G',

        'c7g.xlarge - 4cpu arm 8G',
        'm7g.xlarge - 4cpu arm 16G',
        'r7g.xlarge - 4cpu arm 32G',

        'c7g.2xlarge - 8cpu arm 16G',
        'm7g.2xlarge - 8cpu arm 32G',
        'r7g.2xlarge - 8cpu arm 64G',

        'c7g.4xlarge - 16cpu arm 32G',
        'm7g.4xlarge - 16cpu arm 64G',
        'r7g.4xlarge - 16cpu arm 128G',

        'c7g.8xlarge - 32cpu arm 64G',
        'm7g.8xlarge - 32cpu arm 128G',
        'r7g.8xlarge - 32cpu arm 256G',

        'c7g.16xlarge - 64cpu arm 128G',
        'm7g.16xlarge - 64cpu arm 256G',
        'r7g.16xlarge - 64cpu arm 512G',
        ],

    'x86': [
        't3a.nano - 2cpu 0.5G',
        't3a.micro - 2cpu 1G',
        't3a.small - 2cpu 2G',
        't3a.medium - 2cpu 4G',
        't3a.large - 2cpu 8G',

        't3a.xlarge - 4cpu 16G',

        'c6a.2xlarge - 8cpu 16G',
        'm6a.2xlarge - 8cpu 32G',
        'r6a.2xlarge - 8cpu 64G',

        'c6a.4xlarge - 16cpu 32G',
        'm6a.4xlarge - 16cpu 64G',
        'r6a.4xlarge - 16cpu 128G',

        'c6a.8xlarge - 32cpu 64G',
        'm6a.8xlarge - 32cpu 128G',
        'r6a.8xlarge - 32cpu 256G',

        'c6a.16xlarge - 64cpu 128G',
        'm6a.16xlarge - 64cpu 256G',
        'r6a.16xlarge - 64cpu 512G',

        'c6a.32xlarge - 128cpu 256G',
        'm6a.32xlarge - 128cpu 512G',
        'r6a.32xlarge - 128cpu 1024G',

        'c6a.48xlarge - 192cpu 384G',
        'm6a.48xlarge - 192cpu 768G',
        'r6a.48xlarge - 192cpu 1536G',
        ],

    'gpu': [
        'g5.xlarge - 4cpu 16G +GPU',
        'g5.2xlarge - 8cpu 32G +GPU',
        'g5.4xlarge - 16cpu 64G +GPU',
        ],

    'mac': [], # TODO find some mac choices
    }


name = 'EC2'

ec2 = boto3.client('ec2')

class ListFrame(ListBase):
    def thr_get_data(self):
        response = ec2.describe_security_groups()
        sec_grp_names = {}
        for g in response['SecurityGroups']:
            sec_grp_names[g['GroupId']] = self.tag_name(g)
        response = ec2.describe_instances()
        self.clear_list()
        self.instance_ips = {}
        while True:
            for resp in response['Reservations']:
                for i in resp['Instances']:
                    # fill in while listing net ifs
                    self.instance_ips[i['InstanceId']] = {'ipv4': '', 'ipv6': '', 'dns': ''}
                    # if i['State']['Code'] > 255: # clear top byte ?
                    nt = self.tag_name(i)
                    if nt == '': nt = 'Unnamed'
                    item = ttk.Frame(self, borderwidth=2, relief=tk.RIDGE)
                    item.pack(side=tk.TOP, expand=True, fill=tk.X)
                    # name
                    l = ttk.Button(item, text=nt, bootstyle='link',
                                command=lambda tx=nt: self.copy_to_clip(tx))
                    l.grid(row=0, column=0, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Name tag of EC2 instance')

                    # inst id
                    l = ttk.Button(item, text=i['InstanceId'], bootstyle='link',
                                command=lambda tx=i['InstanceId']: self.copy_to_clip(tx))
                    l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Instance ID')

                    # vpcid
                    if 'VpcId' in i:
                        l = ttk.Button(item, text=i['VpcId'], bootstyle='link',
                                    command=lambda tx=i['VpcId']: self.copy_to_clip(tx))
                        l.grid(row=0, column=2, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='VPC ID')

                    # type
                    if i['State']['Code'] == States.TERMINATED:
                        l = ttk.Label(item, text=i['InstanceType'], bootstyle='danger')
                        l.grid(row=1, column=0, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Waiting for AWS to cleanup this resource.')
                    else:
                        l = ttk.Button(item, text=i['InstanceType'], bootstyle='link',
                                    command=lambda iid=i['InstanceId'],
                                            it=i['InstanceType'], ia=i['Architecture']:
                                        self.change_type(iid, it, ia))
                        l.grid(row=1, column=0, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Instance Type.\nClick to change.')

                    # cores/arch
                    cpus = int(i['CpuOptions']['CoreCount']) * int(i['CpuOptions']['ThreadsPerCore'])
                    txt = f'''{cpus} / {i['Architecture']}'''
                    l = ttk.Button(item, text=txt, bootstyle='link',
                                command=lambda tx=txt: self.copy_to_clip(tx))
                    l.grid(row=1, column=1, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Number of cpus / cpu arch')

                    # az
                    txt = i['Placement']['AvailabilityZone']
                    l = ttk.Button(item, text=txt, bootstyle='link',
                                command=lambda tx=txt: self.copy_to_clip(tx))
                    l.grid(row=1, column=2, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Availability zone')

                    # state
                    if i['State']['Code'] == States.TERMINATED:
                        s_style = 'danger' # green
                    elif i['State']['Code'] != States.STOPPED:
                        s_style = 'success-link' # green
                    else:
                        s_style = 'link'
                    if i['State']['Code'] == States.TERMINATED:
                        l = ttk.Label(item, text=i['State']['Name'], bootstyle=s_style)
                        l.grid(row=2, column=0, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Waiting for AWS to cleanup this resource.')
                    else:
                        l = ttk.Button(item, text=i['State']['Name'], bootstyle=s_style,
                                    command=lambda iid=i['InstanceId'], istate=i['State']['Code'], iname=nt:
                                        self.change_state(iid, istate, iname))
                        l.grid(row=2, column=0, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Instance state.\nClick to change.')

                    # key
                    l = ttk.Button(item, text=i['KeyName'], bootstyle='link',
                                command=lambda tx=i['KeyName']: self.copy_to_clip(tx))
                    l.grid(row=2, column=2, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Name of SSH Key')

                    # ssh into
                    b = ttk.Button(item, text='start SSH', bootstyle='primary-outline')
                    b.configure(command=lambda iid=i['InstanceId'], btn=b:
                                        self.ssh_into(iid, btn=btn))
                    b.grid(row=3, column=0, sticky=tk.W, padx=PADDING, pady=PADDING)
                    tt = ToolTip(b, text='Open a terminal and start SSH to this server')
                    if i['State']['Code'] != States.RUNNING:
                        b['state'] = tk.DISABLED

                    # key path
                    if i['InstanceId'] in Opts.known_keys:
                        l = ttk.Button(item,
                                    text=Opts.known_keys[i['InstanceId']],
                                    bootstyle='link',
                                    command=lambda tx=Opts.known_keys[i['InstanceId']]:
                                        self.copy_to_clip(tx))
                        l.grid(row=3, column=2, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Path to SSH Key')

                    # ip address
                    l = ttk.Label(item, text='Public IPv4:')
                    l.grid(row=20, column=0, sticky=tk.E)
                    if 'PublicIpAddress' in i:
                        self.instance_ips[i['InstanceId']]['ipv4'] = i['PublicIpAddress']
                        l = ttk.Button(item, text=i['PublicIpAddress'], bootstyle='link',
                                    command=lambda tx=i['PublicIpAddress']: self.copy_to_clip(tx))
                        l.grid(row=20, column=1, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Public IPv4 Address')
                    if 'PublicDnsName' in i:
                        self.instance_ips[i['InstanceId']]['dns'] = i['PublicDnsName']
                        l = ttk.Button(item, text=i['PublicDnsName'], bootstyle='link',
                                    command=lambda tx=i['PublicDnsName']: self.copy_to_clip(tx))
                        l.grid(row=20, column=2, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Public IPv4 DNS')

                    # network ifaces
                    net_frame = ttk.Frame(item, borderwidth=1, relief=tk.SOLID, padding=1)
                    net_frame.grid(row=30, column=0, columnspan=5, sticky=tk.NW)
                    for nir,ni in enumerate(i['NetworkInterfaces']):
                        ni_frame = ttk.Frame(net_frame)
                        ni_frame.grid(row=nir, column=0, sticky=tk.W)

                        l = ttk.Label(ni_frame, text='Network Interface:')
                        l.grid(row=0, column=0, sticky=tk.E, padx=PADDING)
                        l = ttk.Button(ni_frame, text=ni['NetworkInterfaceId'], bootstyle='link',
                                command=lambda tx=ni['NetworkInterfaceId']: self.copy_to_clip(tx))
                        l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Network interface ID')

                        # ipv4
                        ## frame
                        ipv4_frame = ttk.Frame(ni_frame)
                        ipv4_frame.grid(row=10, column=0, columnspan=5, sticky=tk.W)
                        for row,ip4 in enumerate(ni['PrivateIpAddresses']):
                            l = ttk.Button(ipv4_frame, text=ip4['PrivateIpAddress'], bootstyle='link',
                                        command=lambda tx=ip4['PrivateIpAddress']: self.copy_to_clip(tx))
                            l.grid(row=row, column=0, sticky=tk.E)
                            tt = ToolTip(l, text='Private IP address')
                            l = ttk.Button(ipv4_frame, text=ip4['PrivateDnsName'], bootstyle='link',
                                        command=lambda tx=ip4['PrivateDnsName']: self.copy_to_clip(tx))
                            l.grid(row=row, column=1, sticky=tk.W)
                            tt = ToolTip(l, text='Private DNS name')

                        # ipv6
                        if 'Ipv6Addresses' in ni:
                            ipv6_frame = ttk.Frame(ni_frame)
                            ipv6_frame.grid(row=20, column=0, columnspan=5, sticky=tk.W)
                            if len(ni['Ipv6Addresses']):
                                self.instance_ips[i['InstanceId']]['ipv6'] = \
                                                ni['Ipv6Addresses'][0]['Ipv6Address']
                            for row,ip6 in enumerate(ni['Ipv6Addresses']):
                                l = ttk.Button(ipv6_frame, text=ip6['Ipv6Address'], bootstyle='link',
                                            command=lambda tx=ip6['Ipv6Address']: self.copy_to_clip(tx))
                                l.grid(row=row, column=0)
                                tt = ToolTip(l, text='IPv6 address')

                        # sg
                        sg_frame = ttk.Frame(ni_frame)
                        sg_frame.grid(row=30, column=0, columnspan=5, sticky=tk.W)
                        for row,sg in enumerate(ni['Groups']):
                            l = ttk.Button(sg_frame, text=sg['GroupId'], bootstyle='link',
                                        command=lambda tx=sg['GroupId']: self.copy_to_clip(tx))
                            l.grid(row=row, column=0, sticky=tk.E)
                            tt = ToolTip(l, text='Security group ID')
                            sg_tag_name = sec_grp_names[sg['GroupId']]
                            l = ttk.Button(sg_frame, text=sg_tag_name, bootstyle='link',
                                        command=lambda tx=sg_tag_name: self.copy_to_clip(tx))
                            l.grid(row=row, column=1, sticky=tk.W)
                            tt = ToolTip(l, text='Security group name tag')
                            l = ttk.Button(sg_frame, text=sg['GroupName'], bootstyle='link',
                                        command=lambda tx=sg['GroupName']: self.copy_to_clip(tx))
                            l.grid(row=row, column=2, sticky=tk.W)
                            tt = ToolTip(l, text='Security group name')

            if 'NextToken' in response and response['NextToken'] is not None:
                response = ec2.describe_instances(NextToken=response['NextToken'])
            else:
                break

    def change_state(self, inst_id, inst_state, inst_name):
        w = tk.Toplevel(self)
        w.title('Change state to:')
        w.resizable(0,0)

        def start():
            try:
                ec2.start_instances(InstanceIds=[inst_id])
            except Exception as e:
                print(e)
            w.destroy()
            self.after(5000, self.refresh())

        def restart():
            ec2.reboot_instances(InstanceIds=[inst_id])
            w.destroy()

        def stop():
            ec2.stop_instances(InstanceIds=[inst_id])
            w.destroy()

        def force_stop():
            ec2.stop_instances(InstanceIds=[inst_id], Force=True)
            w.destroy()

        l = ttk.Label(w, text='Instance:')
        l.grid(row=0, column=0, sticky=tk.E, padx=PADDING)
        l = ttk.Label(w, text=inst_id)
        l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
        l = ttk.Label(w, text='Name:')
        l.grid(row=1, column=0, sticky=tk.E, padx=PADDING)
        l = ttk.Label(w, text=inst_name)
        l.grid(row=1, column=1, sticky=tk.W, padx=PADDING)
        bf = ttk.Frame(w)
        bf.grid(row=10, column=0, columnspan=2, sticky=tk.EW, pady=PADDING)
        bf.columnconfigure(0, weight=1)
        bf.columnconfigure(2, weight=1)
        # start
        if inst_state == States.STOPPED:
            b = ttk.Button(bf, text='Start', command=start, bootstyle='success-outline')
            b.grid(row=10, column=1, sticky=tk.EW, padx=PADDING, pady=PADDING)
        # force restart
        b = ttk.Button(bf, text='Restart', command=restart, bootstyle='danger-outline')
        b.grid(row=20, column=1, sticky=tk.EW,  padx=PADDING, pady=PADDING)
        # stop
        b = ttk.Button(bf, text='Stop', command=stop, bootstyle='danger-outline')
        b.grid(row=30, column=1, sticky=tk.EW,  padx=PADDING, pady=PADDING)
        # force stop
        b = ttk.Button(bf, text='Force Stop', command=force_stop, bootstyle='danger-outline')
        b.grid(row=40, column=1, sticky=tk.EW,  padx=PADDING, pady=PADDING)

    def change_type(self, inst_id, inst_type, inst_arch):
        w = tk.Toplevel(self)
        w.title('Change Type to:')
        w.resizable(0,0)

        l = ttk.Label(w, text='Instance:')
        l.grid(row=0, column=0, sticky=tk.E, padx=PADDING)
        l = ttk.Label(w, text=inst_id)
        l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)

        l = ttk.Label(w, text='Current Type:')
        l.grid(row=1, column=0, sticky=tk.E, padx=PADDING)
        l = ttk.Label(w, text=inst_type)
        l.grid(row=1, column=1, sticky=tk.W, padx=PADDING)

        l = ttk.Label(w, text='Change to:')
        l.grid(row=2, column=0, sticky=tk.E, padx=PADDING)
        if inst_arch == 'x86_64':
            if inst_type.startswith('g5'):
                type_options = TYPE_CHOICES['gpu']
            else:
                type_options = TYPE_CHOICES['x86']
        elif inst_arch == 'arm64':
            type_options = TYPE_CHOICES['arm']
        else:
            type_options = ['Unknown arch']
        target_type = tk.StringVar()
        target_type.set([t for t in type_options if t.startswith(inst_type)][0])
        cb = ttk.Combobox(w, textvariable=target_type, values=type_options, width=30)
        cb.grid(row=2, column=1, sticky=tk.W, padx=PADDING)

        def make_change():
            if target_type.get() not in TYPE_CHOICES['x86'] + TYPE_CHOICES['arm'] + TYPE_CHOICES['gpu']:
                print('nope')
                return
            ec2.modify_instance_attribute(InstanceId=inst_id,
                            InstanceType={'Value': target_type.get().split(' ')[0]})
            w.destroy()
            self.after(5000, self.refresh())

        b = ttk.Button(w, text='Change', command=make_change)
        b.grid(row=999, column=1, sticky=tk.E, padx=PADDING, pady=PADDING)

    def ssh_into(self, inst_id, btn):
        '''
        scp -6 -o IdentitiesOnly=yes -i key_path ec2-user@\[xxxx\]:Downs/file ./
        '''
        key_path = ''
        username = 'ec2-user'
        if inst_id in Opts.known_keys:
            username = Opts.known_keys[inst_id][0]
            key_path = f'-i {Opts.known_keys[inst_id][1]}'
        if self.instance_ips[inst_id]['ipv6'] != '':
            ssh_cmd = f'''ssh -t -6 -o IdentitiesOnly=yes {key_path} {username}@{self.instance_ips[inst_id]['ipv6']}''' #+ ';exec ${SHELL} ' # to keep term open
        elif self.instance_ips[inst_id]['dns'] != '':
            ssh_cmd = f'ssh -t -o IdentitiesOnly=yes {key_path} {username}@'+self.instance_ips[inst_id]['dns']
        elif self.instance_ips[inst_id]['ipv4'] != '':
            ssh_cmd = f'ssh -t -o IdentitiesOnly=yes {key_path} {username}@'+self.instance_ips[inst_id]['ipv4']
        else:
            mb.ok('Unable to ssh without an ip address', title='No IP Address', parent=btn)
            return
        if Opts.run_tmux:
            ssh_cmd += ' tmux'
        if Opts.develop: print('cmd will be :-' + ssh_cmd)
        if Opts.terminal == 'gnome-terminal':
            sp.Popen([Opts.terminal , '--window', '--', 'sh', '-c', ssh_cmd])
        elif Opts.terminal == 'xterm':
            sp.Popen([Opts.terminal , '-e', ssh_cmd])
        else:
            mb.ok('Unknown shell choice.', title='Unknown Shell', parent=btn)

