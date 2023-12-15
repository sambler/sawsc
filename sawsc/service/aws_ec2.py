
import boto3
from enum import Enum
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip

from . import ListBase

Opts = None # set from gui when making ListFrame
PADDING = 2

class States(Enum):
    # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html
    PENDING = 0
    RUNNING = 16
    SHUTTING_DOWN = 32
    TERMINATED = 48
    STOPPING = 64
    STOPPED = 80

name = 'EC2'

ec2 = boto3.client('ec2')

class ListFrame(ListBase):
    def thr_get_data(self):
        response = ec2.describe_instances()
        self.clear_list()
        while True:
            for resp in response['Reservations']:
                for i in resp['Instances']:
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
                    l = ttk.Button(item, text=i['VpcId'], bootstyle='link',
                                command=lambda tx=i['VpcId']: self.copy_to_clip(tx))
                    l.grid(row=0, column=2, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='VPC ID')

                    # type
                    l = ttk.Button(item, text=i['InstanceType'], bootstyle='link',
                                command=lambda tx=i['InstanceType']: self.copy_to_clip(tx))
                    l.grid(row=1, column=0, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Instance Type')

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
                    i_state = int(i['State']['Code'])
                    if i_state != States.STOPPED:
                        s_style = 'success-link' # green
                    else:
                        s_style = 'link'
                    l = ttk.Button(item, text=i['State']['Name'], bootstyle=s_style,
                                command=lambda tx=i['State']['Name']: self.copy_to_clip(tx))
                    l.grid(row=2, column=0, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Instance state')

                    # key
                    l = ttk.Button(item, text=i['KeyName'], bootstyle='link',
                                command=lambda tx=i['KeyName']: self.copy_to_clip(tx))
                    l.grid(row=2, column=2, sticky=tk.W, padx=PADDING)
                    tt = ToolTip(l, text='Name of SSH Key')

                    # ip address
                    l = ttk.Label(item, text='Public IPv4:')
                    l.grid(row=20, column=0, sticky=tk.E)
                    if 'PublicIpAddress' in i:
                        l = ttk.Button(item, text=i['PublicIpAddress'], bootstyle='link',
                                    command=lambda tx=i['PublicIpAddress']: self.copy_to_clip(tx))
                        l.grid(row=20, column=1, sticky=tk.W, padx=PADDING)
                        tt = ToolTip(l, text='Public IPv4 Address')
                    if 'PublicDnsName' in i:
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
                            l = ttk.Button(sg_frame, text=sg['GroupName'], bootstyle='link',
                                        command=lambda tx=sg['GroupName']: self.copy_to_clip(tx))
                            l.grid(row=row, column=1, sticky=tk.W)
                            tt = ToolTip(l, text='Security group name')

            if 'NextToken' in response and response['NextToken'] is not None:
                response = ec2.describe_instances(NextToken=response['NextToken'])
            else:
                break

