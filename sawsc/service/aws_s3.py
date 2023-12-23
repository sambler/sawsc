#
#  aws_s3.py
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
