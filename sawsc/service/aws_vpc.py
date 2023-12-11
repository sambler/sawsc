
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.tooltip import ToolTip

Opts = None # set from gui when making ListFrame

name = 'VPC'

class ListFrame(ttk.Frame):
    def __init__(self, par):
        super().__init__(par)
        l = ttk.Label(self, text=f' {name} data here')
        l.grid(row=0, column=0)

