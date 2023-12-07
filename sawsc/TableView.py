#
#  __init__.py for TableView widget module
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


import sys
import tkinter as tk
from tkinter import ttk

# options items are changed to tk variables at runtime
# change option values with Options.val.set()
class Options:
    scrollspeed = 6 # tk.IntVar for FrameList - osx==1

class TableView(tk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self._listItems = {}
        self._rowcount = 0
        self._columncount = 0
        self._show_vert_scroll = tk.BooleanVar()
        self._show_vert_scroll.set(True)
        self._show_horiz_scroll = tk.BooleanVar()
        self._show_horiz_scroll.set(True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        Options.scrollspeed = tk.IntVar()
        Options.scrollspeed.set(6)
        # setup scrollable area
        self._canvas = tk.Canvas(self)
        self.scrollhoriz = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        self.scrollhoriz.grid(row=1, column=0, sticky=tk.EW)
        self.scrollvert = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self.scrollvert.grid(row=0, column=1, sticky=tk.NS)
        self._scrollable_frame = ttk.Frame(self._canvas)
        self._scrollable_frame.bind('<Configure>',
                lambda e: self._canvas.configure(
                    scrollregion=self._canvas.bbox(tk.ALL)))
        self._canvas.create_window((0,0), window=self._scrollable_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=self.scrollvert.set)
        self._canvas.configure(xscrollcommand=self.scrollhoriz.set)
        self._canvas.grid(row=0, column=0, sticky=tk.NSEW)

        self.bind('<Enter>', self._bindwheel)
        self.bind('<Leave>', self._unbindwheel)

    def _bindwheel(self, event=None):
        if sys.platform.startswith('osx') or sys.platform.startswith('win'):
            self._canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        else:
            self._canvas.bind_all('<Button-4>', self._on_mousewheel)
            self._canvas.bind_all('<Button-5>', self._on_mousewheel)

    def _unbindwheel(self, event=None):
        if sys.platform.startswith('osx') or sys.platform.startswith('win'):
            self._canvas.unbind_all('<MouseWheel>')
        else:
            self._canvas.unbind_all('<Button-4>')
            self._canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event=None):
        if event.num == 4 or event.delta == 120:
            if event.state == 24:
                self._canvas.xview_scroll(int(-2-(1/Options.scrollspeed.get())), 'units')
            else:
                self._canvas.yview_scroll(int(-2-(1/Options.scrollspeed.get())), 'units')
        elif event.num == 5 or event.delta == -120:
            if event.state == 24:
                self._canvas.xview_scroll(int(2+(1/Options.scrollspeed.get())), 'units')
            else:
                self._canvas.yview_scroll(int(2+(1/Options.scrollspeed.get())), 'units')

    def idx(self, row, col):
        return f'row{row}:col{col}'

    def show_horiz_scroll(self, evnt=None):
        self._show_horiz_scroll.set(True)
        self.scrollhoriz.grid(row=1, column=0, sticky=tk.EW)

    def hide_horiz_scroll(self, evnt=None):
        self._show_horiz_scroll.set(False)
        self.scrollhoriz.grid_forget()

    def toggle_horiz_scroll(self, evnt=None):
        self._show_horiz_scroll.set(not self._show_horiz_scroll.get())
        if self._show_horiz_scroll.get():
            self.show_horiz_scroll()
        else:
            self.hide_horiz_scroll()

    def show_vert_scroll(self, evnt=None):
        self._show_vert_scroll.set(True)
        self.scrollvert.grid(row=0, column=1, sticky=tk.NS)

    def hide_vert_scroll(self, evnt=None):
        self._show_vert_scroll.set(False)
        self.scrollvert.grid_forget()

    def toggle_vert_scroll(self, evnt=None):
        self._show_vert_scroll.set(not self._show_vert_scroll.get())
        if self._show_vert_scroll.get():
            self.show_vert_scroll()
        else:
            self.hide_vert_scroll()

    def clear_list_items(self, evnt=None):
        for i in self._listItems.keys():
            if i.startswith('row'):
                #print(f'destroying {i}')
                self._listItems[i].destroy()
        self._listItems = {}

    def clear_item_at(self, row, col):
        idx = self.idx(row, col)
        if idx in self._listItems:
            self._listItems[idx].destroy()
            del self._listItems[idx]

    def set_column_width(self, col, width):
        col_idx = f'colw:{col}'
        self._listItems[col_idx] = width

    def list_item_at(self, row, col):
        if row > self._rowcount: self._rowcount = row
        if col > self._columncount: self._columncount = col
        idx = self.idx(row, col)
        if idx not in self._listItems:
            col_idx = f'colw:{col}'
            if col_idx in self._listItems:
                self._listItems[idx] = ttk.Label(self._scrollable_frame,
                                            width=self._listItems[col_idx],
                                            anchor=tk.W)
            else:
                self._listItems[idx] = ttk.Label(self._scrollable_frame,
                                            anchor=tk.W)
            self._listItems[idx].mytable = self
            self._listItems[idx].myrow = row
            self._listItems[idx].mycol = col
            self._listItems[idx].grid(row=row, column=col)
        return self._listItems[idx]

    def set_item_at(self, row, col, wdgt):
        if row > self._rowcount: self._rowcount = row
        if col > self._columncount: self._columncount = col
        idx = self.idx(row, col)
        if idx in self._listItems:
            del self._listItems[idx]
        wdgt.mytable = self
        wdgt.myrow = row
        wdgt.mycol = col
        wdgt.grid(row=row, column=col)
        self._listItems[idx] = wdgt
