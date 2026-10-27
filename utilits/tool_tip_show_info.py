import tkinter as tk

class CreateToolTip:
    """
    Создаёт всплывающую подсказку для заданного виджета.
    Использует только стандартный tkinter, без внешних зависимостей.
    """
    def __init__(self, widget, text='подсказка'):
        self.widget = widget
        self.text = text
        self.waittime = 500  # задержка перед показом в миллисекундах
        self.wraplength = 180  # ширина подсказки в пикселях
        self.id = None
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # без рамки и заголовка
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tw, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            wraplength=self.wraplength
        )
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
            self.tw = None
