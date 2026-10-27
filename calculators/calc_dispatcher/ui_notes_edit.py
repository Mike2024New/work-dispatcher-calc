import tkinter as tk


class Config:
    FONT_LABEL = ("Segoe UI", 14)
    FONT_ENTRY = ("Segoe UI", 14)
    FONT_BUTTON = ("Segoe UI Semibold", 14)
    COLOR_BG = "#f0f0f0"
    COLOR_LABEL = "#222222"
    COLOR_ENTRY_BG = "#ffffff"
    COLOR_ENTRY_FG = "#000000"
    COLOR_BUTTON_BG = "#4a90e2"
    COLOR_BUTTON_FG = "#ffffff"
    PAD_X = 10
    PAD_Y = 8
    ENTRY_WIDTH = 90
    BUTTON_WIDTH = 4


class NotesEditor(tk.Toplevel):
    def __init__(self, notes):
        super().__init__()
        self.title("Редактор примечаний")
        self.configure(bg=Config.COLOR_BG)
        self.notes = notes
        self.entries = []
        self.result = None  # сюда положим итоговый список, если применили изменения

        self.container = tk.Frame(self, bg=Config.COLOR_BG)
        self.container.pack(padx=Config.PAD_X, pady=Config.PAD_Y, fill="both", expand=True)

        self.render_notes()

        buttons_frame = tk.Frame(self, bg=Config.COLOR_BG)
        buttons_frame.pack(pady=(10, 15))

        self.apply_btn = tk.Button(
            buttons_frame,
            text="Применить",
            command=self.apply,
            font=Config.FONT_BUTTON,
            bg=Config.COLOR_BUTTON_BG,
            fg=Config.COLOR_BUTTON_FG,
            activebackground="#357ABD",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            width=15
        )
        self.apply_btn.pack(side="left", padx=10)

        self.add_btn = tk.Button(
            buttons_frame,
            text="Добавить",
            command=self.add_note,
            font=Config.FONT_BUTTON,
            bg="#27ae60",
            fg=Config.COLOR_BUTTON_FG,
            activebackground="#219150",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            width=15
        )
        self.add_btn.pack(side="left", padx=10)

        # Обработка закрытия окна (например, крестиком)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def render_notes(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.entries.clear()

        for idx, note in enumerate(self.notes):
            frame = tk.Frame(self.container, bg=Config.COLOR_BG)
            frame.pack(fill="x", pady=4)

            label = tk.Label(
                frame,
                text=f"{idx + 1}.",
                font=Config.FONT_LABEL,
                fg=Config.COLOR_LABEL,
                bg=Config.COLOR_BG,
                width=4,
                anchor="w"
            )
            label.pack(side="left")

            entry = tk.Entry(
                frame,
                font=Config.FONT_ENTRY,
                fg=Config.COLOR_ENTRY_FG,
                bg=Config.COLOR_ENTRY_BG,
                width=Config.ENTRY_WIDTH
            )
            entry.insert(0, note)
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self.entries.append(entry)

            btn_del = tk.Button(
                frame,
                text="-",
                font=Config.FONT_BUTTON,
                bg="#e74c3c",
                fg="#ffffff",
                activebackground="#c0392b",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                width=Config.BUTTON_WIDTH,
                command=lambda i=idx: self.delete_note(i)
            )
            btn_del.pack(side="left", padx=5)

        self.update_idletasks()
        self.geometry("")  # Автоматически подстраиваем размер окна

    def delete_note(self, index):
        self.notes.pop(index)
        self.render_notes()

    def add_note(self):
        self.notes.append("")
        self.render_notes()

    def apply(self):
        self.result = [entry.get() for entry in self.entries]
        self.destroy()  # закрываем окно

    def on_close(self):
        # Если окно закрыто без применения, результат None
        self.result = None
        self.destroy()


def edit_notes(notes, parent=None):
    app1 = NotesEditor(notes)
    if parent:
        app1.transient(parent)  # окно поверх родителя
        app1.grab_set()         # блокируем родителя
    app1.wait_window()          # ждем закрытия окна
    return app1.result



if __name__ == "__main__":
    from utilits.work_json import read_json_file, rec_json_file
    import os

    file_path = os.path.join(os.getcwd(), 'ui_notes.json')
    notes_list = read_json_file(
        file_path=file_path
    )['notes']
    updated_notes = edit_notes(notes_list)
    if updated_notes is not None:
        updated_notes = [note for note in updated_notes if note.strip() != ""]
        rec_json_file(
            file_path=file_path,
            data={"notes": updated_notes}
        )
