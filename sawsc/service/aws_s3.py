
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.tooltip import ToolTip

from . import ListBase

Opts = None # set from gui when making ListFrame

name = 'S3'

class ListFrame(ListBase):
    def thr_get_data(self):
        self.clear_list()
        l = ttk.Label(self, text=f' {name} data here')
        l.grid(row=0, column=0)

