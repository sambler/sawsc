
import boto3
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip

from . import ListBase

name = 'EC2 snapshots'

Opts = None # set from gui when making ListFrame
PADDING = 2

ec2 = boto3.client('ec2')

class ListFrame(ListBase):
    def thr_get_data(self):
        vpcs = ec2.describe_snapshots(OwnerIds=[Opts.aws_customer_id.get()])
        self.clear_list()
        while True:
            for s in vpcs['Snapshots']:
                nt = [t['Value'] for t in s['Tags'] if t['Key'] == 'Name'][0]
                if nt == '': nt = 'Unnamed'
                item = ttk.Frame(self, borderwidth=2, relief=tk.RIDGE)
                item.pack(side=tk.TOP, expand=True, fill=tk.X)
                # name
                l = ttk.Button(item, text=nt, bootstyle='link',
                            command=lambda tx=nt: self.copy_to_clip(tx))
                l.grid(row=0, column=0, sticky=tk.W, padx=PADDING)
                tt = ToolTip(l, text='Name tag of snapshot')

                l = ttk.Button(item, text=s['SnapshotId'], bootstyle='link',
                            command=lambda tx=s['SnapshotId']: self.copy_to_clip(tx))
                l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
                tt = ToolTip(l, text='Snapshot ID')

                l = ttk.Button(item, text=s['VolumeId'], bootstyle='link',
                            command=lambda tx=s['VolumeId']: self.copy_to_clip(tx))
                l.grid(row=0, column=2, sticky=tk.W, padx=PADDING)
                tt = ToolTip(l, text='VolumeId snapshot was created from')

                # size
                l = ttk.Label(item, text='Size:')
                l.grid(row=1, column=0, sticky=tk.E, padx=PADDING)
                l = ttk.Button(item, text=s['VolumeSize'], bootstyle='link',
                            command=lambda tx=s['VolumeSize']: self.copy_to_clip(tx))
                l.grid(row=1, column=1, sticky=tk.W, padx=PADDING)

                # start time
                l = ttk.Label(item, text='Created:')
                l.grid(row=2, column=0, sticky=tk.E, padx=PADDING)
                l = ttk.Button(item, text=s['StartTime'], bootstyle='link',
                            command=lambda tx=s['StartTime']: self.copy_to_clip(tx))
                l.grid(row=2, column=1, sticky=tk.W, padx=PADDING)

                # frame for tags
                if len(s['Tags']) > 1 or (len(s['Tags']) ==1 and s['Tags'][0]['Key'] != 'Name'):
                    l = ttk.Label(item, text='Tags:')
                    l.grid(row=9, column=0, sticky=tk.E, padx=PADDING)
                    t_frame = ttk.Frame(item)
                    t_frame.grid(row=10, column=0, columnspan=10, sticky=tk.NW)
                    for r,t in enumerate(s['Tags']):
                        if t['Key'] == 'Name': continue
                        l = ttk.Label(t_frame, text=t['Key'])
                        l.grid(row=r, column=0, sticky=tk.E, padx=PADDING)
                        l = ttk.Button(t_frame, text=t['Value'], bootstyle='link',
                                command=lambda tx=t['Value']: self.copy_to_clip(tx))
                        l.grid(row=r, column=1, sticky=tk.W, padx=PADDING)

            if 'NextToken' in vpcs and vpcs['NextToken'] is not None:
                vpcs = ec2.describe_vpcs(NextToken=vpcs['NextToken'])
            else:
                break

