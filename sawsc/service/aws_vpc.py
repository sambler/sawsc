
import boto3
from pprint import pp
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.tooltip import ToolTip

from . import ListBase

name = 'VPC'

Opts = None # set from gui when making ListFrame
PADDING = 2

ec2 = boto3.client('ec2')

class ListFrame(ListBase):
    def thr_get_data(self):
        vpcs = ec2.describe_vpcs()
        self.clear_list()
        while True:
            for v in vpcs['Vpcs']:
                nt = [t['Value'] for t in v['Tags'] if t['Key'] == 'Name'][0]
                if nt == '': nt = 'Unnamed'
                item = ttk.Frame(self, borderwidth=2, relief=tk.RIDGE)
                item.pack(side=tk.TOP, expand=True, fill=tk.X)
                # name
                l = ttk.Button(item, text=nt, bootstyle='link', command=lambda tx=nt: self.copy_to_clip(tx))
                l.grid(row=0, column=0, sticky=tk.W, padx=PADDING)
                # VpcId
                l = ttk.Button(item, text=v['VpcId'], bootstyle='link', command=lambda tx=v['VpcId']: self.copy_to_clip(tx))
                l.grid(row=0, column=2, sticky=tk.W, padx=PADDING)
                # CidrBlock
                l = ttk.Button(item, text=v['CidrBlock'], bootstyle='link', command=lambda tx=v['CidrBlock']: self.copy_to_clip(tx))
                l.grid(row=1, column=0, sticky=tk.W, padx=PADDING)
                # Ipv6CidrBlockAssociationSet - Ipv6CidrBlock
                if 'Ipv6CidrBlockAssociationSet' in v:
                    ip6f = ttk.Frame(item)
                    ip6f.grid(row=1, column=2)
                    for r,ip6bas in enumerate(v['Ipv6CidrBlockAssociationSet']):
                        l = ttk.Button(ip6f, text=ip6bas['Ipv6CidrBlock'], bootstyle='link', command=lambda tx=ip6bas['Ipv6CidrBlock']: self.copy_to_clip(tx))
                        l.grid(row=r, column=0, sticky=tk.W, padx=PADDING)
                else:
                    l = ttk.Label(item, text='No IPv6 CIDR')
                    l.grid(row=1, column=2, padx=PADDING, pady=PADDING)
            if 'NextToken' in vpcs and vpcs['NextToken'] is not None:
                vpcs = ec2.describe_vpcs(NextToken=vpcs['NextToken'])
            else:
                break

