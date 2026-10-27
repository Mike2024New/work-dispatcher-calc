import os
import tkinter as tk
import tkinter.messagebox as messagebox


class Config:
    FONT_LABEL = ("Segoe UI", 11)
    FONT_HEADER = ("Segoe UI Semibold", 14)  # шрифт для заголовка
    FONT_ENTRY = ("Segoe UI", 11)
    FONT_BUTTON = ("Segoe UI Semibold", 12)
    COLOR_BG = "#e6e6e6"
    COLOR_LABEL = "#333333"
    COLOR_ENTRY_BG = "#ffffff"
    COLOR_ENTRY_FG = "#000000"
    COLOR_BUTTON_BG = "#4a90e2"
    COLOR_BUTTON_FG = "#ffffff"
    COLOR_ACTIVE_BUTTON_BG = "red"
    COLOR_ACTIVE_BUTTON_FG = "red"  # исправлена опечатка
    PAD_X = 8
    PAD_Y = 6
    ENTRY_WIDTH = 25
    SPINBOX_WIDTH = 12


class App(tk.Toplevel):
    def __init__(self, directory, description="test", callback=lambda: print("заглушка")):
        super().__init__()
        self.directory = directory
        self.callback = callback
        self.description = description

        self.title("Редактор конфигурации калькулятора")
        # self.geometry("480x400")  # убран фиксированный размер
        self.configure(bg=Config.COLOR_BG)

        self.blocks_container = tk.Frame(self, bg=Config.COLOR_BG)
        self.blocks_container.pack(fill="both", expand=True, padx=12, pady=12)

        # Заголовок жирным шрифтом
        self.header_label = tk.Label(
            self,
            text="Инструкция",
            font=Config.FONT_HEADER,
            fg=Config.COLOR_LABEL,
            bg=Config.COLOR_BG
        )
        self.header_label.pack(pady=(10, 5))

        # Описание
        self.label = tk.Label(
            self,
            text=self.description,
            font=Config.FONT_LABEL,
            fg=Config.COLOR_LABEL,
            bg=Config.COLOR_BG,
            wraplength=440,
            justify="left"
        )
        self.label.pack(pady=(10, 15))

        # Кнопка открыть папку с прайс листом
        self.btn_open_folder = tk.Button(
            self,
            text="Папка",
            command=self.open_directory,
            font=Config.FONT_BUTTON,
            bg=Config.COLOR_BUTTON_BG,
            fg=Config.COLOR_BUTTON_FG,
            activebackground=Config.COLOR_ACTIVE_BUTTON_BG,
            activeforeground=Config.COLOR_ACTIVE_BUTTON_FG,
            relief=tk.FLAT,
            padx=10,
            pady=6,
            width=30
        )
        self.btn_open_folder.pack(pady=(10, 15))

        self.btn_apply = tk.Button(
            self,
            text="Обновить",
            command=self.apply,
            font=Config.FONT_BUTTON,
            bg=Config.COLOR_BUTTON_BG,
            fg=Config.COLOR_BUTTON_FG,
            activebackground=Config.COLOR_ACTIVE_BUTTON_BG,
            activeforeground=Config.COLOR_ACTIVE_BUTTON_FG,
            relief=tk.FLAT,
            padx=10,
            pady=6,
            width=30
        )
        self.btn_apply.pack(pady=(10, 15))

        self.update_idletasks()  # обновляем геометрию

    def open_directory(self):
        try:
            os.startfile(self.directory)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{e}")

    def apply(self):
        self.callback()
        messagebox.showinfo("Успех", "Выполнено!")
        self.destroy()


def start(directory, txt, callback):
    app = App(directory, txt, callback)
    app.mainloop()


txt = """
1) Нажмите кнопку "папка". Откроется папка с файлом в котором лежит прайс-лист.
2) Удалите старый прайс-лист (или отредактируйте цены в существующем). Закройте папку.
3) Нажмите кнопку "обновить".
4) Подождите пока не появится окно об успешном обновлении.
Готово!
-------------------------------------------------------------------------
На вход принимаются файлы в формате .txt, название может быть любое, но файл 
в папке должен быть 1.
"""

if __name__ == '__main__':
    from calculators.calc_dispatcher.main import DispatcherCalcManager

    disp_manager = DispatcherCalcManager(
        directory=os.getcwd()
    )
    start(
        directory=os.path.join(os.getcwd(), 'base', 'price'),
        txt=txt,
        callback=disp_manager.update_price_ui
    )
