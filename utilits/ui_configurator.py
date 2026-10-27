import os
import tkinter as tk
import tkinter.messagebox as messagebox
from utilits.work_json import read_json_file, edit_json_value


class Config:
    FONT_LABEL = ("Segoe UI", 11)
    FONT_ENTRY = ("Segoe UI", 11)
    FONT_BUTTON = ("Segoe UI Semibold", 12)
    COLOR_BG = "#e6e6e6"
    COLOR_LABEL = "#333333"
    COLOR_ENTRY_BG = "#ffffff"
    COLOR_ENTRY_FG = "#000000"
    COLOR_BUTTON_BG = "#4a90e2"
    COLOR_BUTTON_FG = "#ffffff"
    PAD_X = 8
    PAD_Y = 6
    ENTRY_WIDTH = 25
    SPINBOX_WIDTH = 12


class LabelEntryBlock(tk.Frame):
    def __init__(self, master, key, label_text, field_value=None, field_type="entry", **kwargs):
        super().__init__(master, **kwargs)
        self.key = key
        self.field_type = field_type

        self.configure(bg=Config.COLOR_BG)

        self.label = tk.Label(self, text=label_text, font=Config.FONT_LABEL, fg=Config.COLOR_LABEL, bg=Config.COLOR_BG)
        self.label.grid(row=0, column=0, sticky="w", padx=Config.PAD_X, pady=Config.PAD_Y)

        if field_type == "entry":
            self.var = tk.StringVar()
            if field_value is not None:
                self.var.set(field_value)
            self.widget = tk.Entry(self, textvariable=self.var, font=Config.FONT_ENTRY,
                                   bg=Config.COLOR_ENTRY_BG, fg=Config.COLOR_ENTRY_FG,
                                   width=Config.ENTRY_WIDTH, relief=tk.FLAT)
            self.widget.grid(row=0, column=1, sticky="ew", padx=Config.PAD_X, pady=Config.PAD_Y)

        elif field_type == "spinbox":
            self.var = tk.DoubleVar()
            if field_value is not None:
                try:
                    self.var.set(float(field_value))
                except (ValueError, TypeError):
                    self.var.set(0.0)
            self.widget = tk.Spinbox(self, increment=1.0, textvariable=self.var, width=Config.SPINBOX_WIDTH,
                                     font=Config.FONT_ENTRY, bg=Config.COLOR_ENTRY_BG, fg=Config.COLOR_ENTRY_FG,
                                     relief=tk.FLAT)
            self.widget.grid(row=0, column=1, sticky="ew", padx=Config.PAD_X, pady=Config.PAD_Y)

        elif field_type == "checkbutton":
            self.var = tk.BooleanVar()
            if field_value is not None:
                self.var.set(bool(field_value))
            self.widget = tk.Checkbutton(self, variable=self.var, bg=Config.COLOR_BG)
            self.widget.grid(row=0, column=1, sticky="w", padx=Config.PAD_X, pady=Config.PAD_Y)

        else:
            raise ValueError(f"Unsupported field_type: {field_type}")

        self.columnconfigure(1, weight=1)

    def get_value(self):
        return self.var.get()

    def set_value(self, value):
        self.var.set(value)


class App(tk.Toplevel):
    def __init__(self, configure_json_path):
        super().__init__()
        self.title("Редактор конфигурации калькулятора")
        self.geometry("480x400")
        self.configure(bg=Config.COLOR_BG)

        self.blocks_container = tk.Frame(self, bg=Config.COLOR_BG)
        self.blocks_container.pack(fill="both", expand=True, padx=12, pady=12)

        self.blocks = []

        self.configure_json_path = configure_json_path
        self.data = read_json_file(file_path=self.configure_json_path)
        for row, key in enumerate(self.data):
            self.add_block(
                key=key,
                label_text=self.data[key]["label"],
                field_value=self.data[key]["value"],
                field_type=self.data[key]["field_type"],
                row=row
            )

        self.apply_button = tk.Button(self, text="Применить", command=self.apply,
                                      font=Config.FONT_BUTTON,
                                      bg=Config.COLOR_BUTTON_BG, fg=Config.COLOR_BUTTON_FG,
                                      activebackground="#357ABD", activeforeground="#ffffff",
                                      relief=tk.FLAT, padx=10, pady=6)
        self.apply_button.pack(pady=(10, 15))

    def add_block(self, key, label_text, field_value=None, field_type='entry', row=0):
        block = LabelEntryBlock(
            self.blocks_container,
            key=key,
            label_text=label_text,
            field_value=field_value,
            field_type=field_type,
            bg=Config.COLOR_BG
        )
        block.grid(row=row, column=0, sticky="ew", pady=4)
        self.blocks.append(block)
        self.blocks_container.grid_columnconfigure(0, weight=1)

    def apply(self):
        for block in self.blocks:
            value = block.get_value()
            self.data[block.key]["value"] = value
        for k, v in self.data.items():
            edit_json_value(
                file_path=self.configure_json_path,
                key_path=k,
                new_value=self.data[k]
            )
        messagebox.showinfo("Успех", "Данные успешно изменены!")
        self.destroy()


def start(configure_json_path,parent=None):
    app = App(configure_json_path=configure_json_path)
    app.transient(parent)
    app.grab_set()
    app.wait_window()

    # app1 = NotesEditor(notes)
    # if parent:
    #     app1.transient(parent)  # окно поверх родителя
    #     app1.grab_set()         # блокируем родителя
    # app1.wait_window()          # ждем закрытия окна
    # return app1.result


if __name__ == '__main__':
    start(configure_json_path=os.path.join(os.getcwd(), "ui_parametrs.json"))
