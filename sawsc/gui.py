#
#  gui.py
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
import json
import os
import sawsc
import sys
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from ttkbootstrap import toast
from ttkbootstrap.tooltip import ToolTip
#from ttkbootstrap import validator, add_validation

PADDING = 5

Opts = None # created in gui init()

# service as class_name: display_name
KNOWN_SERVICES = {
    'AWSvpc': 'VPC',
    'AWSec2': 'EC2',
    'AWSs3': 'S3',
    }


class AWSvpc(ttk.Frame):
    def __init__(self, par):
        super().__init__(par)
        l = ttk.Label(self, text=' VPC data here')
        l.grid(row=0, column=0)


class AWSec2(ttk.Frame):
    def __init__(self, par):
        super().__init__(par)
        l = ttk.Label(self, text=' EC2 data here')
        l.grid(row=0, column=0)


class AWSs3(ttk.Frame):
    def __init__(self, par):
        super().__init__(par)
        l = ttk.Label(self, text=' S3 data here')
        l.grid(row=0, column=0)


class AppOptions:
    def __init__(self):
        self.develop = tk.BooleanVar()
        self.develop.set(False)
        self._active_theme = 'darkly'
        self.active_choice = tk.StringVar()
        self.active_choice.set('AWSec2')
        self.remember_service = tk.BooleanVar()
        self.remember_service.set(False)
        self.load()

    @property
    def active_theme(self):
        return self._active_theme

    @active_theme.setter
    def active_theme(self, val):
        self._active_theme = val
        ttk.Style(self.active_theme)

    @property
    def config_file(self):
        # TODO adjust per platform
        return os.path.join(os.path.expanduser('~'), '.config', 'sawsc', 'config.json')

    def defaults(self):
        return {'Appearance': {'theme': 'darkly',},
                'State': {'service': 'AWSec2', 'remember': False}
                }

    def save(self):
        config = self.defaults()
        config['Appearance']['theme'] = self.active_theme
        config['State']['service'] = self.active_choice.get()
        config['State']['remember'] = self.remember_service.get()
        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        with open(self.config_file, 'w') as conf_file:
            conf_file.write(json.dumps(config, indent=4))

    def load(self):
        config = self.defaults()
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as conf_file:
                config = json.loads(conf_file.read())
        if 'Appearance' not in config: config['Appearance'] = {}
        if 'State' not in config: config['State'] = {}
        self.active_theme = config['Appearance'].get('theme', 'darkly')
        ttk.Style(self.active_theme)
        self.active_choice.set(config['State'].get('service', 'AWSec2'))
        self.remember_service.set(config['State'].get('remember', False))


class SawscPrefs(tk.Toplevel):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self.title('Sawsc Preferences')
        self.minsize(width=200, height=150)
        self.grid()
        lbl = ttk.Label(self, text='')
        lbl.grid(row=0, column=0)

        lbl = ttk.Label(self, text='Development:')
        lbl.grid(row=10, column=0, padx=3, sticky=tk.E)
        # store to allow test activate
        self.dev_opt = ttk.Checkbutton(self, variable=Opts.develop, command=self.change_dev)
        self.dev_opt.grid(row=10, column=1, sticky=tk.W)

        lbl = ttk.Label(self, text='Theme:')
        lbl.grid(row=20, column=0, padx=3, sticky=tk.E)
        self.theme_choice = tk.StringVar()
        self.theme_choice.set(Opts.active_theme)
        theme_options = [t for t in ttk.Style().theme_names()]
        cb = ttk.Combobox(self, textvariable=self.theme_choice, values=theme_options)
        cb.grid(row=20, column=1, sticky=tk.W)
        cb.bind('<<ComboboxSelected>>', self.change_style)

        lbl = ttk.Label(self, text='Remember service:')
        lbl.grid(row=30, column=0, padx=3, sticky=tk.E)
        rs = ttk.Checkbutton(self, variable=Opts.remember_service)
        rs.grid(row=30, column=1, sticky=tk.W)

        b = ttk.Button(self, text='Save', bootstyle='success', command=self.save)
        b.grid(row=900, column=1, sticky=tk.SE, padx=PADDING*2, pady=PADDING)
        self.rowconfigure(900, weight=1)

    def change_dev(self, evnt=None):
        self.master.show_develop()

    def change_style(self, evnt=None):
        Opts.active_theme = self.theme_choice.get()

    def save(self, evnt=None):
        Opts.save()
        self.destroy()


class SawscGUI(tk.Tk):
    def __init__(self):
        global Opts
        super().__init__()
        self.title('Sawsc')
        self.minsize(width=500, height=400)
        if Opts is None:
            Opts = AppOptions()
        self.develop_notice = None
        self.bind('<Control-q>', self.quitkey)
        self.add_menus()
        self.layout()

    def add_menus(self):
        self.mainmenu = tk.Menu(self)

        # File
        self.filemenu = tk.Menu(self.mainmenu, tearoff=0)
        #self.filemenu.add_command(label='New Resource',
        #        command=self.menu_new_resource, accelerator='Ctrl+N')
        #self.filemenu.add_separator()
        self.filemenu.add_command(label='Preferences',
                command=self.menu_preferences)

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

    def layout(self):
        self.button_list = ScrolledFrame(self, padding=0)
        self.button_list.grid(row=0, column=0, sticky=tk.NS)

        max_b_width = 0
        for r,s in enumerate(KNOWN_SERVICES):
            b = ttk.Radiobutton(self.button_list, text=KNOWN_SERVICES[s], value=s,
                            variable=Opts.active_choice,
                            command=self.change_service,
                            bootstyle='toolbutton')
            b.grid(row=r, column=0, sticky=EW)
            b.update()
            max_b_width = max(max_b_width, b.winfo_width())
        self.button_list.container['width'] = max_b_width + 11

        self.info_view = ScrolledFrame(self)
        self.info_view.grid(row=0, column=1, sticky=tk.NSEW)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)

        self.change_service()

    def change_service(self, evnt=None):
        for c in self.info_view.winfo_children():
            c.destroy()
        nview = globals()[Opts.active_choice.get()](self.info_view)
        nview.grid(row=0, column=1, sticky=tk.NSEW)
        if Opts.remember_service.get():
            Opts.save()

    def about_me(self, evnt=None):
        mb.ok('Setup and manage AWS resources.', title='About')

    def menu_preferences(self, evnt=None):
        w = SawscPrefs(self)

    def quitkey(self, evnt=None):
        self.destroy()

    def show_develop(self, evnt=None):
        if Opts.develop.get():
            if self.develop_notice is None:
                self.develop_notice = ttk.Label(self, text='DEVELOPMENT',
                        font=('Dejavu Sans', 12, 'bold'), foreground='red')
            self.develop_notice.place(x=-17, y=1, relx=1, anchor=tk.NE)
            self.develop_notice.lift()
        else:
            if self.develop_notice is not None:
                self.develop_notice.destroy()
                self.develop_notice = None

    def main(self, args=None):
        self.show_develop()
        return self.mainloop()


def main(args=None):
    mw = SawscGUI()
    Opts.develop.set(('-d' in sys.argv) or ('--debug' in sys.argv))
    sys.exit(mw.main(sys.argv))


if __name__ == '__main__':
    print() # start output on a new line
    main()

