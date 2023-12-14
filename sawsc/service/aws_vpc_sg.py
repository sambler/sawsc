
import boto3
import tkinter as tk
import ttkbootstrap as ttk

from . import ListBase

name = 'VPC Security Groups'

Opts = None # set from gui when making ListFrame
PADDING = 2

ec2 = boto3.client('ec2')

class ListFrame(ListBase):
    def thr_get_data(self):
        sgs = ec2.describe_security_groups()
        self.clear_list()
        while True:
            for g in sgs['SecurityGroups']:
                nt = [t['Value'] for t in g['Tags'] if t['Key'] == 'Name'][0]
                if nt == '': nt = 'Unnamed'
                item = ttk.Frame(self, borderwidth=2, relief=tk.RIDGE)
                item.pack(side=tk.TOP, expand=True, fill=tk.X)
                # tagged name
                l = ttk.Button(item, text=nt, bootstyle='link',
                            command=lambda tx=nt: self.copy_to_clip(tx))
                l.grid(row=0, column=0, sticky=tk.W, padx=PADDING)
                # SG id
                l = ttk.Button(item, text=g['GroupId'], bootstyle='link',
                            command=lambda tx=g['GroupId']: self.copy_to_clip(tx))
                l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                # VpcId
                l = ttk.Button(item, text=g['VpcId'], bootstyle='link',
                            command=lambda tx=g['VpcId']: self.copy_to_clip(tx))
                l.grid(row=0, column=2, sticky=tk.W, padx=PADDING)
                # desc
                l = ttk.Button(item, text=g['Description'], bootstyle='link',
                            command=lambda tx=g['Description']: self.copy_to_clip(tx))
                l.grid(row=2, column=0, columnspan=5, sticky=tk.W, padx=PADDING)
                rules_frame = ttk.Frame(item)
                rules_frame.grid(row=10, column=0, columnspan=10, sticky=tk.EW, padx=PADDING, pady=PADDING)
                # inbound rules
                l = ttk.Label(rules_frame, text='Inbound Allow:')
                l.grid(row=0, column=0, sticky=tk.W, padx=PADDING)
                in_rules = ttk.Frame(rules_frame)
                in_rules.grid(row=1, column=0, sticky=tk.NW, padx=PADDING, pady=PADDING)
                for r,rule in enumerate(g['IpPermissions']):
                    r_frame = ttk.Frame(in_rules, borderwidth=1, relief=tk.SOLID, padding=1)
                    r_frame.grid(row=r+1, column=0)
                    l = ttk.Label(r_frame, text='From port:')
                    l.grid(row=0, column=0, sticky=tk.E, padx=PADDING)
                    if 'FromPort' in rule:
                        l = ttk.Button(r_frame, text=rule['FromPort'], bootstyle='link',
                                command=lambda tx=rule['FromPort']: self.copy_to_clip(tx))
                        l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                    l = ttk.Label(r_frame, text='To port:')
                    l.grid(row=1, column=0, sticky=tk.E, padx=PADDING)
                    if 'ToPort' in rule:
                        l = ttk.Button(r_frame, text=rule['ToPort'], bootstyle='link',
                                command=lambda tx=rule['ToPort']: self.copy_to_clip(tx))
                        l.grid(row=1, column=1, sticky=tk.W, padx=PADDING)
                    l = ttk.Label(r_frame, text='Protocol:')
                    l.grid(row=2, column=0, sticky=tk.E, padx=PADDING)
                    l = ttk.Button(r_frame, text=rule['IpProtocol'], bootstyle='link',
                            command=lambda tx=rule['IpProtocol']: self.copy_to_clip(tx))
                    l.grid(row=2, column=1, sticky=tk.W, padx=PADDING)
                    ip4_frame = ttk.Frame(r_frame)
                    ip4_frame.grid(row=3, column=0, columnspan=5)
                    for ir,ip4 in enumerate(rule['IpRanges']):
                        l = ttk.Button(ip4_frame, text=ip4['CidrIp'], bootstyle='link',
                            command=lambda tx=ip4['CidrIp']: self.copy_to_clip(tx))
                        l.grid(row=ir, column=0, padx=PADDING)
                        if 'Description' in ip4:
                            l = ttk.Button(ip4_frame, text=ip4['Description'], bootstyle='link',
                                command=lambda tx=ip4['Description']: self.copy_to_clip(tx))
                            l.grid(row=ir, column=1, padx=PADDING)
                    ip6_frame = ttk.Frame(r_frame)
                    ip6_frame.grid(row=5, column=0, columnspan=5)
                    for ir,ip6 in enumerate(rule['Ipv6Ranges']):
                        l = ttk.Button(ip6_frame, text=ip6['CidrIpv6'], bootstyle='link',
                            command=lambda tx=ip6['CidrIpv6']: self.copy_to_clip(tx))
                        l.grid(row=ir, column=0, padx=PADDING)
                        if 'Description' in ip6:
                            l = ttk.Button(ip6_frame, text=ip6['Description'], bootstyle='link',
                                command=lambda tx=ip6['Description']: self.copy_to_clip(tx))
                            l.grid(row=ir, column=1, padx=PADDING)
                # outbound rules
                l = ttk.Label(rules_frame, text='Outbound Allow:')
                l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                out_rules = ttk.Frame(rules_frame)
                out_rules.grid(row=1, column=1, sticky=tk.NE, padx=PADDING, pady=PADDING)
                for r,rule in enumerate(g['IpPermissionsEgress']):
                    r_frame = ttk.Frame(out_rules, borderwidth=1, relief=tk.SOLID, padding=1)
                    r_frame.grid(row=r+1, column=0)
                    l = ttk.Label(r_frame, text='From port:')
                    l.grid(row=0, column=0, sticky=tk.E, padx=PADDING)
                    if 'FromPort' in rule:
                        l = ttk.Button(r_frame, text=rule['FromPort'], bootstyle='link',
                                command=lambda tx=rule['FromPort']: self.copy_to_clip(tx))
                        l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                    l = ttk.Label(r_frame, text='To port:')
                    l.grid(row=1, column=0, sticky=tk.E, padx=PADDING)
                    if 'ToPort' in rule:
                        l = ttk.Button(r_frame, text=rule['ToPort'], bootstyle='link',
                                command=lambda tx=rule['ToPort']: self.copy_to_clip(tx))
                        l.grid(row=1, column=1, sticky=tk.W, padx=PADDING)
                    l = ttk.Label(r_frame, text='Protocol:')
                    l.grid(row=2, column=0, sticky=tk.E, padx=PADDING)
                    l = ttk.Button(r_frame, text=rule['IpProtocol'], bootstyle='link',
                            command=lambda tx=rule['IpProtocol']: self.copy_to_clip(tx))
                    l.grid(row=2, column=1, sticky=tk.W, padx=PADDING)
                    ip4_frame = ttk.Frame(r_frame)
                    ip4_frame.grid(row=3, column=0, columnspan=5)
                    for ir,ip4 in enumerate(rule['IpRanges']):
                        l = ttk.Button(ip4_frame, text=ip4['CidrIp'], bootstyle='link',
                            command=lambda tx=ip4['CidrIp']: self.copy_to_clip(tx))
                        l.grid(row=ir, column=0, padx=PADDING)
                        if 'Description' in ip4:
                            l = ttk.Button(ip4_frame, text=ip4['Description'], bootstyle='link',
                                command=lambda tx=ip4['Description']: self.copy_to_clip(tx))
                            l.grid(row=ir, column=1, padx=PADDING)
                    ip6_frame = ttk.Frame(r_frame)
                    ip6_frame.grid(row=5, column=0, columnspan=5)
                    for ir,ip6 in enumerate(rule['Ipv6Ranges']):
                        l = ttk.Button(ip6_frame, text=ip6['CidrIpv6'], bootstyle='link',
                            command=lambda tx=ip6['CidrIpv6']: self.copy_to_clip(tx))
                        l.grid(row=ir, column=0, padx=PADDING)
                        if 'Description' in ip6:
                            l = ttk.Button(ip6_frame, text=ip6['Description'], bootstyle='link',
                                command=lambda tx=ip6['Description']: self.copy_to_clip(tx))
                            l.grid(row=ir, column=1, padx=PADDING)
            if 'NextToken' in sgs and sgs['NextToken'] is not None:
                sgs = ec2.describe_security_groups(NextToken=sgs['NextToken'])
            else:
                break
