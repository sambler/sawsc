#
#  __init__.py
#
#  Copyright (c)2022 Shane Ambler <Develop@ShaneWare.biz>
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
import sys


class BotoConfig():
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        # self.grid()
        # lbl = ttk.Label(self, text='')
        # lbl.grid(row=0, column=0)

        # lbl = ttk.Label(self, text='Region:')
        # lbl.grid(row=10, column=0, padx=3, sticky=tk.E)
        # val = ttk.Checkbutton(self, variable=APP_WIN.develop, command=self.dev_change)
        # val.grid(row=10, column=1, sticky=tk.W)

        # lbl = ttk.Label(self, text='Scroll speed:')
        # lbl.grid(row=500, column=0, padx=3, sticky=tk.E)
        # val = ttk.Entry(self, textvariable=APP_WIN.scrollspeed)
        # val.grid(row=500, column=1, sticky=tk.W)

        # lbl = ttk.Label(self, text='')
        # lbl.grid(row=999, column=0)

'''

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#guide-configuration


https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-regions-avail-zones.html
get region list

client = boto3.client('ec2')

# Retrieves all regions/endpoints that work with EC2
response = client.describe_regions()

# Retrieves availability zones only for region of the ec2 object
response = client.describe_availability_zones()

regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

'''
