#
#  gui.py
#
#  Copyright (c)2022 Shane Ambler <Develop@ShaneWare.biz>
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


import sawsc
import sys
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

DEBUG = True
TOOL_WIDTH = 5


class ScrollableFrame(ttk.Frame):
    """
    Scrollable Frame, to hold a scrollable list of frames
    call add_to_list(myframe) to add your custom frames to this list
    """
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        # setup scrollable area
        self._canvas = tk.Canvas(self)
        scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        self._scrollable_frame = ttk.Frame(self._canvas, width=300, height=300)

        self._scrollable_frame.bind('<Configure>',
                lambda e: self._canvas.configure(
                    scrollregion=self._canvas.bbox(tk.ALL)))

        self._canvas.create_window((0,0), window=self._scrollable_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar_y.set)
        self._canvas.configure(xscrollcommand=scrollbar_x.set)
        self._canvas.grid(row=0, column=0, sticky=tk.NSEW)

        scrollbar_y.grid(row=0, column=1, sticky=tk.NS)
        scrollbar_x.grid(row=1, column=0, sticky=tk.EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._canvas.update_idletasks()

        self.bind('<Enter>', self._bindwheel)
        self.bind('<Leave>', self._unbindwheel)

    def canvasx(self, inx):
        return self._canvas.canvasx(inx)

    def canvasy(self, iny):
        return self._canvas.canvasy(iny)

    def add_to(self, item_cls, pos):
        ni = item_cls(self._scrollable_frame)
        ni.place(x=pos[0], y=pos[1], anchor=tk.NW)
        return ni # return obj so we can keep a reference

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
            self._canvas.yview_scroll(int(-2-(1/self.master.scrollspeed.get())), 'units')
        elif event.num == 5 or event.delta == -120:
            self._canvas.yview_scroll(int(2+(1/self.master.scrollspeed.get())), 'units')


class SawscOptions(tk.Toplevel):
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
        self.dev_opt = ttk.Checkbutton(self, variable=self.master.develop, command=self.dev_change)
        self.dev_opt.grid(row=10, column=1, sticky=tk.W)

        lbl = ttk.Label(self, text='Scroll speed:')
        lbl.grid(row=500, column=0, padx=3, sticky=tk.E)
        val = ttk.Spinbox(self, textvariable=self.master.scrollspeed, from_=1, to=20, width=5)
        val.grid(row=500, column=1, sticky=tk.W)


    def dev_change(self, evnt=None):
        self.master.show_develop()


class SawscRsrc(tk.Canvas):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.dragging = True
        self.config(width=80, height=80, bg=None)
        self.fill_colour = 'blue'
        self.border_colour = 'DarkBlue'

    # adapted from https://stackoverflow.com/a/61162928/2684771
    def _draw(self):

        ratioMultiplier = 1
        ratioDividend = 2

        x = [0, int(self.cget('width')), int(self.cget('width')), 0]
        y = [0, 0, int(self.cget('height')), int(self.cget('height'))]
        # Array to store the points
        points = []

        # Iterate over the x points
        for i in range(len(x)):
            # Set vertex
            points.append(x[i])
            points.append(y[i])

            # If it's not the last point
            if i != (len(x) - 1):
                # Insert submultiples points. The more the sharpness, the more these points will be
                # closer to the vertex.
                points.append((ratioMultiplier*x[i] + x[i + 1])/ratioDividend)
                points.append((ratioMultiplier*y[i] + y[i + 1])/ratioDividend)
                points.append((ratioMultiplier*x[i + 1] + x[i])/ratioDividend)
                points.append((ratioMultiplier*y[i + 1] + y[i])/ratioDividend)
            else:
                # Insert submultiples points.
                points.append((ratioMultiplier*x[i] + x[0])/ratioDividend)
                points.append((ratioMultiplier*y[i] + y[0])/ratioDividend)
                points.append((ratioMultiplier*x[0] + x[i])/ratioDividend)
                points.append((ratioMultiplier*y[0] + y[i])/ratioDividend)
                # Close the polygon
                points.append(x[0])
                points.append(y[0])

        self.create_polygon(points, smooth=True, fill=self.fill_colour)


class SawscRegion(SawscRsrc):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.fill_colour='#99ccff'
        self._draw()


class SawscVPC(SawscRsrc):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.fill_colour='#ffffcc'
        self._draw()


class SawscNet(SawscRsrc):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.fill_colour='#ccccff'
        self._draw()


class SawscEC2(SawscRsrc):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.fill_colour='#33cc33'
        self._draw()


class SawscRDS(SawscRsrc):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.fill_colour='#ff9933'
        self._draw()


class SawscAPI(SawscRsrc):
    def __init__(self, par, **kwargs):
        super().__init__(par)
        self.fill_colour='#ff99ff'
        self._draw()


class SawscPalette(ttk.Frame):
    def __init__(self, par, **kwargs):
        super().__init__(par, **kwargs)
        self._drag_item = None
        self.palette_button(0, 0, 'Rgn', SawscRegion)
        self.palette_button(0, 1, 'Vpc', SawscVPC)
        self.palette_button(1, 0, 'Net', SawscNet)
        self.palette_button(1, 1, 'EC2', SawscEC2)
        self.palette_button(2, 0, 'RDS', SawscRDS)
        self.palette_button(2, 1, 'API', SawscAPI)

    def palette_button(self, row, col, text, cls):
        b = ttk.Button(self, text=text, width=TOOL_WIDTH)
        b.item_class = cls
        b.grid(row=row, column=col)
        b.bind('<Button-1>', self.drag_start)
        b.bind('<B1-Motion>', self.drag_motion)
        b.bind('<ButtonRelease-1>', self.drag_end)
        return b

    def drag_start(self, evnt):
        if self._drag_item is None:
            self._drag_item = evnt.widget.item_class(self.master.display)
            self._drag_item.xadj = self.master.display.winfo_rootx() - evnt.widget.winfo_rootx()
            self._drag_item.yadj = self.master.display.winfo_rooty() - evnt.widget.winfo_rooty()
            xpos = self.master.display.canvasx(evnt.x - self._drag_item.xadj)
            ypos = self.master.display.canvasx(evnt.y - self._drag_item.yadj)
            self._drag_item.place(x=xpos, y=ypos, anchor=tk.NW)
            self.save_cursor = evnt.widget['cursor'] or ''
            evnt.widget['cursor'] = 'hand1'

    def drag_motion(self, evnt):
        if self._drag_item is not None:
            xpos = self.master.display.canvasx(evnt.x - self._drag_item.xadj)
            ypos = self.master.display.canvasx(evnt.y - self._drag_item.yadj)
            self._drag_item.place(x=xpos, y=ypos, anchor=tk.NW)

    def drag_end(self, evnt):
        if self._drag_item is not None:
            evnt.widget['cursor'] = self.save_cursor
            self._drag_item = None


class SawscGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Sawsc')
        self.minsize(width=500, height=400)
        self.develop = tk.BooleanVar()
        self.develop.set(DEBUG)
        self.develop_notice = None

        self.scrollspeed = tk.IntVar()
        if sys.platform.startswith('osx'):
            self.scrollspeed.set(1)
        else:
            self.scrollspeed.set(6)
        self.palette = SawscPalette(self)
        self.palette.grid(row=0, column=0, rowspan=100, sticky=tk.NS)
        self.display = ScrollableFrame(self)
        self.display.grid(row=10, column=10, sticky=tk.NSEW)
        self.columnconfigure(10, weight=1)
        self.rowconfigure(10, weight=1)
        self.add_menus()
        self.bind('<Control-q>', self.quitkey)
        self.show_develop()

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

    def about_me(self, evnt=None):
        mb.showinfo('About', message='Setup and manage AWS resources.')

    def menu_preferences(self, evnt=None):
        w = SawscOptions(self)

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

    def main(self, args=None):
        return self.mainloop()


def main(args=None):
    global DEBUG
    DEBUG = ('-d' in sys.argv) or ('--debug' in sys.argv)
    mw = SawscGUI()
    sys.exit(mw.main(sys.argv))

if __name__ == '__main__':
    print() # start output on a new line
    main()

