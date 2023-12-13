
import tkinter as tk
import ttkbootstrap as ttk

from . import ListBase

Opts = None # set from gui when making ListFrame

name = 'S3'

class ListFrame(ListBase):
    def thr_get_data(self):
        self.clear_list()
        l = ttk.Label(self, text=f' {name} data here')
        l.grid(row=0, column=0)

