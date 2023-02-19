#!/usr/bin/env python3
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


import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb


APP_WIN = None


class ScrollableFrame(ttk.Frame):
    """
    Scrollable Frame, to hold a scrollable list of frames
    call add_to_list(myframe) to add your custom frames to this list
    """
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        # setup scrollable area
        self._canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._scrollable_frame = ttk.Frame(self._canvas)

        self._scrollable_frame.bind('<Configure>',
                lambda e: self._canvas.configure(
                    scrollregion=self._canvas.bbox(tk.ALL)))

        self._canvas.create_window((0,0), window=self._scrollable_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.bind('<Enter>', self._bindwheel)
        self.bind('<Leave>', self._unbindwheel)

    def add_to_list(self, frame_cls):
        frame_cls(self._scrollable_frame).pack(fill=tk.X)

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
            self._canvas.yview_scroll(int(-2-(1/APP_WIN.scrollspeed.get())), 'units')
        elif event.num == 5 or event.delta == -120:
            self._canvas.yview_scroll(int(2+(1/APP_WIN.scrollspeed.get())), 'units')


class SawscOptions(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self.grid()
        lbl = ttk.Label(self, text='')
        lbl.grid(row=0, column=0)

        lbl = ttk.Label(self, text='Development:')
        lbl.grid(row=10, column=0, padx=3, sticky=tk.E)
        # store to allow test activate
        self.dev_opt = ttk.Checkbutton(self, variable=APP_WIN.develop, command=self.dev_change)
        self.dev_opt.grid(row=10, column=1, sticky=tk.W)

        lbl = ttk.Label(self, text='Scroll speed:')
        lbl.grid(row=500, column=0, padx=3, sticky=tk.E)
        val = ttk.Entry(self, textvariable=APP_WIN.scrollspeed)
        val.grid(row=500, column=1, sticky=tk.W)

        lbl = ttk.Label(self, text='')
        lbl.grid(row=999, column=0)

    def dev_change(self, evnt=None):
        APP_WIN.show_develop()


class SawscApp(tk.Tk):
    """
    Window to show config options and actions.

    Create one of these, call add_resource to add each desired resource
    then call mainloop to show the window.
    """
    def __init__(self):
        global APP_WIN
        if APP_WIN is not None: print('multi window')
        APP_WIN = self
        super().__init__()

        self.develop = tk.BooleanVar()
        self.develop.set(True)
        self.develop_notice = None

        self.scrollspeed = tk.IntVar()
        if sys.platform.startswith('osx'):
            APP_WIN.scrollspeed.set(1)
        else:
            APP_WIN.scrollspeed.set(6)
        self._list = ScrollableFrame(self)
        self._list.pack(fill=tk.BOTH, expand=True)
        self._list.add_to_list(SawscOptions)
        self.add_menus()
        self.show_develop()

    def add_menus(self):
        self.mainmenu = tk.Menu(self)

        # File
        self.filemenu = tk.Menu(self.mainmenu, tearoff=0)
        self.filemenu.add_command(label='New Resource',
                command=self.menu_new_resource, accelerator='Ctrl+N')

        self.filemenu.add_separator()
        self.filemenu.add_command(label='Quit',
                command=self.quitkey, accelerator='Ctrl+Q')
        self.mainmenu.add_cascade(label='File', menu=self.filemenu)

        # Help
        self.helpmenu = tk.Menu(self.mainmenu, tearoff=0)
        #self.helpmenu.add_command(label='Documentation', command=self.show_docs)
        self.helpmenu.add_command(label='About',
                command=self.about_me)
        self.mainmenu.add_cascade(label='Help', menu=self.helpmenu)

        self.config(menu=self.mainmenu)

    def about_me(self, evnt=None):
        mb.showinfo('About', message='Setup and manage AWS resources.')

    def quitkey(self, evnt=None):
        self.destroy()

    def menu_new_resource(self, evnt=None):
        pass

    def show_develop(self, evnt=None):
        if self.develop_notice is None:
            if self.develop.get():
                self.develop_notice = ttk.Label(self, text='DEVELOPMENT',
                        font=('Dejavu Sans', 12, 'bold'), foreground='red')
                self.develop_notice.place(x=-17, y=1, relx=1, anchor=tk.NE)
                self.develop_notice.lift()
        else:
            self.develop_notice.destroy()
            self.develop_notice = None

