#
#  service/__init__.py
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

import threading as thr
import tkinter as tk
import ttkbootstrap as ttk


class ListBase(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self.refresh()

    def clear_list(self):
        for c in self.winfo_children():
            c.destroy()

    def copy_to_clip(self, txt):
        self.master.master.master.clipboard_clear()
        self.master.master.master.clipboard_append(txt)
        self.master.master.master.update()

    def tag_name(self, inst):
        if 'Tags' not in inst: return ''
        return [t['Value'] for t in inst['Tags'] if t['Key'] == 'Name'][0]

    def refresh(self):
        t = thr.Thread(target=self.thr_get_data)
        t.daemon = True
        t.start()

    def thr_get_data(self):
        '''
        Override this to get and display specific data
        '''
        self.clear_list()
        l = ttk.Label(self, text=' display data here')
        l.grid(row=0, column=0)


class ItemBase(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)


