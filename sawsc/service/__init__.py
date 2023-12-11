
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox as mb
from ttkbootstrap.tooltip import ToolTip


class ListBase(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)

    def clear_list(self):
        for c in self.winfo_children():
            c.destroy()

    def copy_to_clip(self, txt):
        self.master.master.master.clipboard_clear()
        self.master.master.master.clipboard_append(txt)
        self.master.master.master.update()


class ItemBase(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)


