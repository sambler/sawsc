#
#  __init__.py
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


import json
import os

from . import __version__ as vers

size_suffixes = {1000: ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']}

def hs(size, precision=2, a_k_is_1024=True):
    """
    Convert a computer size to human readable form.

    size -- size in bytes
    a_k_is_1024 --  if True use multiples of 1024
                    if False use multiples of 1000

    returns: string
    """

    B = int(size)

    if B == 1:
        return '1 byte'

    multiple = 1024 if a_k_is_1024 else 1000

    if B < multiple:
        return '{} bytes'.format(B)

    for suffix in size_suffixes[multiple]:
        B /= multiple
        if B < multiple:
            fmt_str = '{:.'+str(precision)+'f} {}'
            return fmt_str.format(B, suffix)

class CLIOptions:
    def __init__(self):
        self.develop = False
        self.active_theme = 'darkly'
        self.active_choice = 'aws_ec2'
        self.aws_customer_id = ''
        self.remember_service = False
        self.run_tmux = True
        self.terminal = ''
        self.known_keys = {}

    @property
    def config_dir(self):
        # TODO adjust per platform
        return os.path.join(os.path.expanduser('~'), '.config', 'sawsc')

    @property
    def config_file(self):
        return os.path.join(self.config_dir, 'config.json')

    def defaults(self):
        return {'Appearance': {'theme': 'darkly',},
                'State': {  'service': 'aws_ec2',
                            'remember': False,
                            'run_tmux': True,
                            },
                'Accounts': {'aws_customer_id': '123465',},
                'Options': {'terminal': 'xterm',},
                'SSH_keys': {}, # as - inst_id: [user, key_path]
                }

    def save(self):
        config = self.defaults()
        config['Appearance']['theme'] = self.active_theme
        config['State']['service'] = self.active_choice
        config['State']['remember'] = self.remember_service
        config['State']['run_tmux'] = self.run_tmux
        config['Accounts']['aws_customer_id'] = self.aws_customer_id
        config['Options']['terminal'] = self.terminal
        config['SSH_keys'] = self.known_keys
        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        with open(self.config_file, 'w') as conf_file:
            conf_file.write(json.dumps(config, indent=4)+'\n')

    def load(self):
        config = self.defaults()
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as conf_file:
                config = json.loads(conf_file.read())
        if 'Appearance' not in config: config['Appearance'] = {}
        if 'State' not in config: config['State'] = {}
        if 'Accounts' not in config: config['Accounts'] = {}
        if 'Options' not in config: config['Options'] = {}
        self.active_theme = config['Appearance'].get('theme', 'darkly')
        self.remember_service = config['State'].get('remember', False)
        if self.remember_service:
            self.active_choice = config['State'].get('service', 'aws_ec2')
        self.run_tmux = config['State'].get('run_tmux', True)
        self.aws_customer_id = config['Accounts'].get('aws_customer_id', '123456')
        self.terminal = config['Options'].get('terminal', 'xterm')
        self.known_keys = config.get('SSH_keys', {})


class GUIOptions(CLIOptions):
    """
    Override properties with tk variable get/set as needed
    """
    def __init__(self):
        #super().__init__() this clobbers properties
        import tkinter as tk
        self._develop = tk.BooleanVar()
        self._develop.set(False)
        self._active_theme = 'darkly'
        self._active_choice = tk.StringVar()
        self._active_choice.set('aws_ec2')
        self._remember_service = tk.BooleanVar()
        self._remember_service.set(False)
        self._run_tmux = tk.BooleanVar()
        self._run_tmux.set(True)
        self._aws_customer_id = tk.StringVar()
        self._terminal = tk.StringVar()
        self.known_keys = {}

    @property
    def active_theme(self):
        return self._active_theme

    @active_theme.setter
    def active_theme(self, val):
        import ttkbootstrap as ttk
        self._active_theme = val
        ttk.Style(self.active_theme)

    @property
    def active_choice(self):
        return self._active_choice.get()

    @active_choice.setter
    def active_choice(self, val):
        self._active_choice.set(val)

    @property
    def aws_customer_id(self):
        return self._aws_customer_id.get()

    @aws_customer_id.setter
    def aws_customer_id(self, val):
        self._aws_customer_id.set(val)

    @property
    def terminal(self):
        return self._terminal.get()

    @terminal.setter
    def terminal(self, val):
        self._terminal.set(val)

    @property
    def develop(self):
        return self._develop.get()

    @develop.setter
    def develop(self, val):
        self._develop.set(val)

    @property
    def remember_service(self):
        return self._remember_service.get()

    @remember_service.setter
    def remember_service(self, val):
        self._remember_service.set(val)

    @property
    def run_tmux(self):
        return self._run_tmux.get()

    @run_tmux.setter
    def run_tmux(self, val):
        self._run_tmux.set(val)

