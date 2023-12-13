
import threading as thr
import tkinter as tk
import ttkbootstrap as ttk


class ListBase(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self.refresh()

    def clear_list(self):
        for c in self.winfo_children():
            c.destroy()

    def copy_to_clip(self, txt):
        print('copy: ' + txt)
        self.master.master.master.clipboard_clear()
        self.master.master.master.clipboard_append(txt)
        self.master.master.master.update()

    def refresh(self):
        t = thr.Thread(target=self.thr_get_data)
        t.daemon = True
        t.start()

    def thr_get_data(self):
        '''
        Override this to get and display specific data
        '''
        self.clear_list()
        l = ttk.Label(self, text=' display data here')
        l.grid(row=0, column=0)


class ItemBase(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)


