
import tkinter as tk
import ttkbootstrap as ttk

from . import ListBase

Opts = None # set from gui when making ListFrame

name = 'EC2'

class ListFrame(ListBase):
    def thr_get_data(self):
        self.clear_list()
        l = ttk.Label(self, text=f' {name} data here')
        l.grid(row=0, column=0)

        if Opts:
            l = ttk.Label(self, text=str(Opts.develop.get()))
            l.grid(row=3, column=0)

