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
from importlib import import_module
import json
import os
import sawsc
import sys
import threading as thr
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview

from . import hs

PADDING = 5

App = None # created in main()

service = {s[:-3]: import_module('sawsc.service.'+s[:-3]) for
                s in sorted(os.listdir(os.path.join(os.path.dirname(
                                    os.path.realpath(__file__)), 'service')))
                if s not in ['__init__.py', '__pycache__']
                }

class tspinner(ttk.Label):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self.frames = '-\|/'
        self.running = False
        self.pos = 0
        self.active_cons = 0

    def start(self):
        self.active_cons += 1
        if not self.running: self.after(300, self.progress)
        self.running = True

    def progress(self):
        if self.active_cons < 1: self.running = False
        if not self.running:
            self['text'] = ''
            return
        self.pos += 1
        if self.pos >= len(self.frames): self.pos = 0
        #self['text'] = str(self.active_cons) + ' ' + self.frames[self.pos]
        self['text'] = self.frames[self.pos]
        self.after(300, self.progress)

    def stop(self):
        self.active_cons -= 1


class AppOptions:
    def __init__(self):
        self.develop = tk.BooleanVar()
        self.develop.set(False)
        self._active_theme = 'darkly'
        self.active_choice = tk.StringVar()
        self.active_choice.set('aws_ec2')
        self.remember_service = tk.BooleanVar()
        self.remember_service.set(False)
        self.aws_customer_id = tk.StringVar()
        self.load()

    @property
    def active_theme(self):
        return self._active_theme

    @active_theme.setter
    def active_theme(self, val):
        self._active_theme = val
        ttk.Style(self.active_theme)

    @property
    def config_dir(self):
        # TODO adjust per platform
        return os.path.join(os.path.expanduser('~'), '.config', 'sawsc')

    @property
    def config_file(self):
        return os.path.join(self.config_dir, 'config.json')

    def defaults(self):
        return {'Appearance': {'theme': 'darkly',},
                'State': {'service': 'aws_ec2', 'remember': False},
                'Accounts': {'aws_customer_id': '123465'},
                }

    def save(self):
        config = self.defaults()
        config['Appearance']['theme'] = self.active_theme
        config['State']['service'] = self.active_choice.get()
        config['State']['remember'] = self.remember_service.get()
        config['Accounts']['aws_customer_id'] = self.aws_customer_id.get()
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
        if 'Accounts' not in config: config['Accounts'] = {}
        self.active_theme = config['Appearance'].get('theme', 'darkly')
        ttk.Style(self.active_theme)
        self.remember_service.set(config['State'].get('remember', False))
        if self.remember_service.get():
            self.active_choice.set(config['State'].get('service', 'aws_ec2'))
        self.aws_customer_id.set(config['Accounts'].get('aws_customer_id', '123456'))


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
        self.dev_opt = ttk.Checkbutton(self, variable=App.opts.develop, command=self.change_dev)
        self.dev_opt.grid(row=10, column=1, sticky=tk.W)

        lbl = ttk.Label(self, text='Theme:')
        lbl.grid(row=20, column=0, padx=3, sticky=tk.E)
        self.theme_choice = tk.StringVar()
        self.theme_choice.set(App.opts.active_theme)
        theme_options = [t for t in ttk.Style().theme_names()]
        cb = ttk.Combobox(self, textvariable=self.theme_choice, values=theme_options)
        cb.grid(row=20, column=1, sticky=tk.W)
        cb.bind('<<ComboboxSelected>>', self.change_style)

        lbl = ttk.Label(self, text='Remember service:')
        lbl.grid(row=30, column=0, padx=3, sticky=tk.E)
        rs = ttk.Checkbutton(self, variable=App.opts.remember_service)
        rs.grid(row=30, column=1, sticky=tk.W)

        lbl = ttk.Label(self, text='AWS customer ID:')
        lbl.grid(row=40, column=0, padx=3, sticky=tk.E)
        rs = ttk.Entry(self, textvariable=App.opts.aws_customer_id)
        rs.grid(row=40, column=1, sticky=tk.W)

        b = ttk.Button(self, text='Save', bootstyle='success', command=self.save)
        b.grid(row=900, column=1, sticky=tk.SE, padx=PADDING*2, pady=PADDING)
        self.rowconfigure(900, weight=1)

    def change_dev(self, evnt=None):
        App.show_develop()

    def change_style(self, evnt=None):
        App.opts.active_theme = self.theme_choice.get()

    def save(self, evnt=None):
        App.opts.save()
        self.destroy()


class SawscRegions(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('AWS Regions')
        self.geometry('300x600')
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.bind('<F5>', self.refresh)
        self.show_all = tk.BooleanVar()
        self.show_all.set=(False)
        self.show_check = ttk.Checkbutton(self, variable=self.show_all,
                                    text='Show all', command=self.refresh)
        self.show_check.grid(row=0, column=0, sticky=tk.W, padx=PADDING, pady=PADDING)
        self.progress = tspinner(self)
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=PADDING)
        self.tree = ScrolledFrame(self)
        self.tree.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.refresh()

    def refresh(self, evnt=None):
        for w in self.tree.winfo_children():
            w.destroy()
        self.show_check['state'] = tk.DISABLED
        t=thr.Thread(target=self.refresh_thread)
        t.daemon = True
        self.progress.start()
        t.start()

    def refresh_thread(self):
        ZONE_INDENT = 5
        ec2 = boto3.client('ec2')
        regions = ec2.describe_regions(AllRegions=self.show_all.get())
        for r_row,rgn in enumerate(sorted(regions['Regions'], key=lambda k: k['RegionName'])):
            f = ttk.Frame(self.tree)
            f.grid(row=r_row*2, column=0, sticky=tk.NSEW)
            l = ttk.Label(f, text=rgn['RegionName'])
            l.grid(row=0, column=0, sticky=tk.NW, padx=PADDING)
            if rgn['OptInStatus'] not in ['opted-in', 'opt-in-not-required', ]:
                l = ttk.Label(f, text=rgn['OptInStatus'])
                l.grid(row=0, column=1, sticky=tk.W, padx=PADDING)
            try:
                z = ttk.Frame(f)
                z.grid(row=(r_row*2)+1, column=0, columnspan=3, sticky=tk.NW)
                zec2 = boto3.client('ec2', region_name=rgn['RegionName'])
                avail_zones = zec2.describe_availability_zones(
                                    AllAvailabilityZones=self.show_all.get())
                for z_row,zone in enumerate(sorted(avail_zones['AvailabilityZones'],
                                                key = lambda k: k['ZoneName'])):
                    l = ttk.Label(z, text='', width=ZONE_INDENT)
                    l.grid(row=z_row, column=0)
                    l = ttk.Label(z, text=zone['ZoneName'])
                    l.grid(row=z_row, column=1, sticky=tk.NW, padx=PADDING)
                    if zone['State'] not in ['available', 'information']:
                        l = ttk.Label(z, text=zone['State'])
                        l.grid(row=z_row, column=2, sticky=tk.W, padx=PADDING)
            except:
                l = ttk.Label(z, text='', width=ZONE_INDENT)
                l.grid(row=0, column=0)
                l = ttk.Label(z, text='Unavailable')
                l.grid(row=0, column=1, sticky=tk.NW, padx=PADDING)
        self.progress.stop()
        self.show_check['state'] = tk.NORMAL

    def close_window(self, evnt=None):
        App.after(100, App.check_windows())
        self.destroy()


class SawscEC2Types(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('AWS EC2 Types')
        self.geometry('900x605')
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.bind('<F5>', self.refresh)
        self.options = ttk.Frame(self)
        self.options.grid(row=0, column=0, sticky=tk.EW)
        self.progress = tspinner(self.options)
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=PADDING)
        st = ttk.Style()
        cols = ['Type', 'arch', 'Manuf.', 'VCPUs', 'Cores', 'Threads',
                'RAM', 'Inst Stg', 'Stg Size',
                'GPU Name', 'GPU Manuf', 'GPU count', 'GPU RAM',
                ]
        self.tree = Tableview(self, coldata=cols, searchable=True,
                                autofit=True,
                                stripecolor=('#403f44', None))
        self.tree.grid(row=1, column=0, sticky=tk.NSEW)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.refresh()

    def refresh(self, evnt=None):
        self.tree.delete_rows()
        t=thr.Thread(target=self.refresh_thread)
        t.daemon = True
        self.progress.start()
        t.start()

    def refresh_thread(self):
        ec2 = boto3.client('ec2')
        inst_types = ec2.describe_instance_types()
        types_data = []
        for inst in inst_types['InstanceTypes']:
            tr = []
            # Type
            tr.append(inst['InstanceType'])
            # arch
            tr.append(','.join(inst['ProcessorInfo']['SupportedArchitectures']))
            # Manufacturer
            tr.append(inst['ProcessorInfo']['Manufacturer'])
            # VCPUs
            tr.append(inst['VCpuInfo']['DefaultVCpus'])
            # Cores
            tr.append(inst['VCpuInfo']['DefaultCores'])
            # Threads
            tr.append(inst['VCpuInfo']['DefaultThreadsPerCore'])
            # RAM - MiB
            tr.append(hs(inst['MemoryInfo']['SizeInMiB']*1024*1024))
            # Inst Storage
            tr.append(inst['InstanceStorageSupported'])
            # Inst Storage size GB
            if 'InstanceStorageInfo' in inst:
                tr.append(hs(inst['InstanceStorageInfo']['TotalSizeInGB']*1024*1024*1024, a_k_is_1024=False))
            else:
                tr.append('')
            # GPU Name
            have_gpuinfo = 'GpuInfo' in inst
            if have_gpuinfo:
                tr.append(','.join([g['Name'] for g in inst['GpuInfo']['Gpus']]))
                # GPU Manuf
                tr.append(','.join([g['Manufacturer'] for g in inst['GpuInfo']['Gpus']]))
                # GPU count
                tr.append(','.join([str(g['Count']) for g in inst['GpuInfo']['Gpus']]))
                # GPU RAM MiB
                tr.append(','.join([hs(g['MemoryInfo']['SizeInMiB']*1024*1024) for g in inst['GpuInfo']['Gpus']]))
            else:
                tr.append('')
                tr.append('')
                tr.append('')
                tr.append('')
            types_data.append(tr)

        self.tree.insert_rows('end', types_data)
        self.tree.reset_table()
        self.tree.autofit_columns()
        self.tree.align_column_right(cid=6)
        self.tree.align_column_right(cid=8)
        self.tree.align_column_right(cid=12)
        self.progress.stop()

    def close_window(self, evnt=None):
        App.after(100, App.check_windows())
        self.destroy()


class SawscGUI(tk.Toplevel):
    def __init__(self):
        global Opts
        super().__init__()
        self.title('Sawsc')
        self.minsize(width=500, height=400)
        self.geometry('850x850')
        self.develop_notice = None
        self.active_choice = tk.StringVar()
        self.active_choice.set(App.opts.active_choice.get())
        self.bind('<Control-n>', self.menu_new_window)
        self.bind('<Control-q>', self.quitkey)
        self.bind('<Control-w>', self.menu_close_window)
        self.protocol("WM_DELETE_WINDOW", self.menu_close_window)
        self.add_menus()
        self.layout()

    def add_menus(self):
        self.mainmenu = tk.Menu(self)

        # File
        self.filemenu = tk.Menu(self.mainmenu, tearoff=0)
        self.filemenu.add_command(label='New Window',
                command=self.menu_new_window, accelerator='Ctrl+N')
        self.filemenu.add_command(label='Close Window',
                command=self.menu_close_window, accelerator='Ctrl+W')
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Preferences',
                command=self.menu_preferences)

        self.filemenu.add_separator()
        self.filemenu.add_command(label='Quit',
                command=self.quitkey, accelerator='Ctrl+Q')
        self.mainmenu.add_cascade(label='File', menu=self.filemenu)

        # info
        self.infomenu = tk.Menu(self.mainmenu, tearoff=0)
        self.infomenu.add_command(label='Regions', command=self.menu_info_regions)
        self.infomenu.add_command(label='EC2 Types', command=self.menu_info_ec2_types)
        self.mainmenu.add_cascade(label='Info', menu=self.infomenu)

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
        for r,s in enumerate(service.keys()):
            b = ttk.Radiobutton(self.button_list, text=service[s].name, value=s,
                            variable=self.active_choice,
                            command=self.change_service,
                            bootstyle='toolbutton')
            b.grid(row=r, column=0, sticky=tk.EW)
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
        service[self.active_choice.get()].Opts = App.opts
        service[self.active_choice.get()].PADDING = PADDING
        nview = service[self.active_choice.get()].ListFrame(self.info_view)
        nview.grid(row=0, column=1, sticky=tk.NSEW)
        if App.opts.remember_service.get():
            App.opts.active_choice.set(self.active_choice.get())
            App.opts.save()

    def about_me(self, evnt=None):
        mb.ok('Setup and manage AWS resources.', title='About')

    def menu_preferences(self, evnt=None):
        w = SawscPrefs(self)

    def menu_new_window(self, evnt=None):
        w = SawscGUI()
        w.show_develop()

    def menu_close_window(self, evnt=None):
        App.after(100, App.check_windows())
        self.destroy()

    def menu_info_regions(self, evnt=None):
        w = SawscRegions()

    def menu_info_ec2_types(self, evnt=None):
        w = SawscEC2Types()

    def quitkey(self, evnt=None):
        App.quit_app()

    def show_develop(self, evnt=None):
        if App.opts.develop.get():
            if self.develop_notice is None:
                self.develop_notice = ttk.Label(self, text='DEVELOPMENT',
                        font=('Dejavu Sans', 12, 'bold'), foreground='red')
            self.develop_notice.place(x=-17, y=1, relx=1, anchor=tk.NE)
            self.develop_notice.lift()
        else:
            if self.develop_notice is not None:
                self.develop_notice.destroy()
                self.develop_notice = None


class AppWindow(tk.Tk):
    def __init__(self):
        global App
        super().__init__()
        self.opts = AppOptions()
        App = self

    def check_windows(self):
        wl = [n for n in self.children]
        if len(wl) < 2:
            self.quit()

    def show_develop(self):
        for w in self.children:
            if isinstance(self.children[w], SawscGUI):
                self.children[w].show_develop()

    def quit_app(self):
        wl = [n for n in self.children]
        for n in wl:
            if isinstance(self.children[n], SawscGUI):
                self.children[n].menu_close_window()
        self.quit()

    def main(self, args=None):
        self.opts.develop.set(('-d' in sys.argv) or ('--debug' in sys.argv))
        fw = SawscGUI()
        fw.show_develop()
        return self.mainloop()


def main(args=None):
    r = AppWindow()
    r.withdraw()
    sys.exit(r.main())


if __name__ == '__main__':
    print() # start output on a new line
    main()

