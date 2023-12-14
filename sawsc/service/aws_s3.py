
import boto3
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip

from . import ListBase

Opts = None # set from gui when making ListFrame

name = 'S3'

s3 = boto3.client('s3')

class ListFrame(ListBase):
    def thr_get_data(self):
        bucket_list = s3.list_buckets()
        self.clear_list()
        for b in bucket_list['Buckets']:
            item = ttk.Frame(self, borderwidth=2, relief=tk.RIDGE)
            item.pack(side=tk.TOP, expand=True, fill=tk.X)
            l = ttk.Button(item, text=b['CreationDate'], bootstyle='link',
                            command=lambda tx=b['CreationDate']: self.copy_to_clip(tx))
            l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
            tt = ToolTip(l, text='Created')
            l = ttk.Button(item, text=b['Name'], bootstyle='link',
                            command=lambda tx=b['Name']: self.copy_to_clip(tx))
            l.grid(row=0, column=2, sticky=tk.W, padx=PADDING)
            tt = ToolTip(l, text='Bucket name')
