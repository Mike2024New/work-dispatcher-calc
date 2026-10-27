import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
import os


class Config:
    BG_MAIN = "#ffffff"
    BG_MODULES = "#e6e6e6"
    BG_OPTIONS_BOX = "#e6e6e6"
    BTN_BG_CALC = "black"
    BTN_FG_CALC = "white"
    BTN_BG_CLEAR = "#555555"
    BTN_FG_CLEAR = "white"
    BTN_BG_ADD = "black"
    BTN_FG_ADD = "white"
    BTN_BG_DEL = "red"
    BTN_FG_DEL = "white"
    LABEL_NUM_FG = "red"


class ItemRow:
    def __init__(self, parent, index, add_callback, remove_callback):
        self.parent = parent
        self.index = index
        self.add_callback = add_callback
        self.remove_callback = remove_callback

        self.num_label = tk.Label(parent, text=str(index), width=3,
                                  fg=Config.LABEL_NUM_FG, bg=Config.BG_MAIN,
                                  font=("Arial", 10, "bold"))

        self.art_entry = tk.Entry(parent, width=20, bg=Config.BG_MODULES, font=("Arial", 11))
        self.name_entry = tk.Entry(parent, width=40, bg=Config.BG_MODULES, font=("Arial", 11))
        self.count_spinbox = tk.Spinbox(parent, from_=0, to=1000000, width=10,
                                        bg=Config.BG_MODULES, font=("Arial", 11))
        self.price_entry = tk.Entry(parent, width=15, bg=Config.BG_MODULES, font=("Arial", 11))

        self.add_btn = tk.Button(parent, text="+", width=3, command=self.on_add,
                                 bg=Config.BTN_BG_ADD, fg=Config.BTN_FG_ADD,
                                 font=("Arial", 10, "bold"), relief="raised")
        self.remove_btn = tk.Button(parent, text="-", width=3, command=self.on_remove,
                                    bg=Config.BTN_BG_DEL, fg=Config.BTN_FG_DEL,
                                    font=("Arial", 10, "bold"), relief="raised")

        self.draw_widgets()

    def draw_widgets(self):
        pady_val = 6
        self.num_label.grid(row=self.index, column=0, padx=3, pady=pady_val, sticky="nsew")
        self.art_entry.grid(row=self.index, column=1, padx=5, pady=pady_val, sticky="ew")
        self.name_entry.grid(row=self.index, column=2, padx=5, pady=pady_val, sticky="ew")
        self.count_spinbox.grid(row=self.index, column=3, padx=5, pady=pady_val, sticky="ew")
        self.price_entry.grid(row=self.index, column=4, padx=5, pady=pady_val, sticky="ew")
        self.add_btn.grid(row=self.index, column=5, padx=5, pady=pady_val)
        self.remove_btn.grid(row=self.index, column=6, padx=5, pady=pady_val)

    def update_index(self, new_index):
        self.index = new_index
        self.num_label.config(text=str(new_index))
        self.draw_widgets()

    def on_add(self):
        self.add_callback(self.index)

    def on_remove(self):
        self.remove_callback(self.index)

    def clear_fields(self):
        self.art_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.count_spinbox.delete(0, tk.END)
        self.count_spinbox.insert(0, "0")
        self.price_entry.delete(0, tk.END)

    def get_data(self):
        art = self.art_entry.get().strip()
        name = self.name_entry.get().strip()
        try:
            count = int(self.count_spinbox.get())
        except ValueError:
            count = 0
        try:
            price = float(self.price_entry.get())
        except ValueError:
            price = 0.0
        return {"art": art, "name": name, "count": int(count), "price": price}

    def set_data(self, data):
        self.art_entry.delete(0, tk.END)
        self.art_entry.insert(0, data.get("art", ""))
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))
        self.count_spinbox.delete(0, tk.END)
        self.count_spinbox.insert(0, str(data.get("count", 0)))
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(data.get("price", 0)))

    def destroy(self):
        self.num_label.destroy()
        self.art_entry.destroy()
        self.name_entry.destroy()
        self.count_spinbox.destroy()
        self.price_entry.destroy()
        self.add_btn.destroy()
        self.remove_btn.destroy()


# ... (EditSetRow и EditSetDialog остаются без изменений, можно вставить из предыдущего кода) ...

class EditSetRow:
    def __init__(self, parent, index, add_callback, remove_callback):
        self.parent = parent
        self.index = index
        self.add_callback = add_callback
        self.remove_callback = remove_callback

        self.num_label = tk.Label(parent, text=str(index), width=3,
                                  fg=Config.LABEL_NUM_FG, bg=Config.BG_MAIN,
                                  font=("Arial", 10, "bold"))

        self.art_entry = tk.Entry(parent, width=20, bg=Config.BG_MODULES, font=("Arial", 11))
        self.name_entry = tk.Entry(parent, width=40, bg=Config.BG_MODULES, font=("Arial", 11))
        self.count_var = tk.StringVar(value="0")
        self.count_entry = tk.Entry(parent, width=15, bg=Config.BG_MODULES, font=("Arial", 11),
                                    textvariable=self.count_var, state="readonly")
        self.price_entry = tk.Entry(parent, width=15, bg=Config.BG_MODULES, font=("Arial", 11))

        self.add_btn = tk.Button(parent, text="+", width=3, command=self.on_add,
                                 bg=Config.BTN_BG_ADD, fg=Config.BTN_FG_ADD,
                                 font=("Arial", 10, "bold"), relief="raised")
        self.remove_btn = tk.Button(parent, text="-", width=3, command=self.on_remove,
                                    bg=Config.BTN_BG_DEL, fg=Config.BTN_FG_DEL,
                                    font=("Arial", 10, "bold"), relief="raised")

        self.draw_widgets()

    def draw_widgets(self):
        pady_val = 6
        self.num_label.grid(row=self.index, column=0, padx=3, pady=pady_val, sticky="nsew")
        self.art_entry.grid(row=self.index, column=1, padx=5, pady=pady_val, sticky="ew")
        self.name_entry.grid(row=self.index, column=2, padx=5, pady=pady_val, sticky="ew")
        self.count_entry.grid(row=self.index, column=3, padx=5, pady=pady_val, sticky="ew")
        self.price_entry.grid(row=self.index, column=4, padx=5, pady=pady_val, sticky="ew")
        self.add_btn.grid(row=self.index, column=5, padx=5, pady=pady_val)
        self.remove_btn.grid(row=self.index, column=6, padx=5, pady=pady_val)

    def update_index(self, new_index):
        self.index = new_index
        self.num_label.config(text=str(new_index))
        self.draw_widgets()

    def on_add(self):
        self.add_callback(self.index)

    def on_remove(self):
        self.remove_callback(self.index)

    def get_data(self):
        art = self.art_entry.get().strip()
        name = self.name_entry.get().strip()
        try:
            price = float(self.price_entry.get())
        except ValueError:
            price = 0.0
        return {"art": art, "name": name, "count": 0, "price": price}

    def set_data(self, data):
        self.art_entry.delete(0, tk.END)
        self.art_entry.insert(0, data.get("art", ""))
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data.get("name", ""))
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(data.get("price", 0)))

    def destroy(self):
        self.num_label.destroy()
        self.art_entry.destroy()
        self.name_entry.destroy()
        self.count_entry.destroy()
        self.price_entry.destroy()
        self.add_btn.destroy()
        self.remove_btn.destroy()


class EditSetDialog(tk.Toplevel):
    def __init__(self, parent, set_name, items):
        super().__init__(parent)
        self.parent = parent
        self.title(f"Редактирование набора: {set_name}")
        self.configure(bg=Config.BG_MAIN)
        self.transient(parent)
        self.grab_set()

        self.set_name = set_name
        self.items = items

        headers = ["№", "Артикул", "Наименование", "Количество (недоступно)", "Цена", "", ""]
        for col, text in enumerate(headers):
            lbl = tk.Label(self, text=text, font=("Arial", 12, "bold"), bg=Config.BG_OPTIONS_BOX)
            lbl.grid(row=0, column=col, padx=5, pady=5, sticky="ew")

        for col in range(7):
            self.grid_columnconfigure(col, weight=1)

        self.rows = []
        self.start_row = 1

        for i, item in enumerate(self.items, start=self.start_row):
            row = EditSetRow(self, i, self.add_row, self.remove_row)
            row.set_data(item)
            self.rows.append(row)

        if not self.rows:
            self.add_row(self.start_row)

        btn_frame = tk.Frame(self, bg=Config.BG_MAIN)
        btn_frame.grid(row=1000, column=0, columnspan=7, pady=10, sticky="ew")

        save_btn = tk.Button(btn_frame, text="Сохранить", command=self.on_save,
                             bg=Config.BTN_BG_CALC, fg=Config.BTN_FG_CALC,
                             font=("Arial", 12, "bold"), relief="raised")
        save_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.on_cancel,
                               bg=Config.BTN_BG_DEL, fg=Config.BTN_FG_DEL,
                               font=("Arial", 12, "bold"), relief="raised")
        cancel_btn.pack(side="left", padx=10)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def add_row(self, index):
        for row in self.rows:
            if row.index >= index:
                row.update_index(row.index + 1)
        new_row = EditSetRow(self, index, self.add_row, self.remove_row)
        self.rows.insert(index - self.start_row, new_row)
        for idx, row in enumerate(self.rows, start=self.start_row):
            row.update_index(idx)

    def remove_row(self, index):
        if len(self.rows) <= 1:
            messagebox.showinfo("Внимание", "Нельзя удалить последнюю строку")
            return
        for i, row in enumerate(self.rows):
            if row.index == index:
                row.destroy()
                self.rows.pop(i)
                break
        for row in self.rows:
            if row.index > index:
                row.update_index(row.index - 1)

    def on_save(self):
        new_items = []
        for row in self.rows:
            data = row.get_data()
            data["count"] = 0
            if not data["art"] or not data["name"]:
                messagebox.showwarning("Ошибка", "Поля 'Артикул' и 'Наименование' не могут быть пустыми.")
                return
            new_items.append(data)
        self.items = new_items
        self.destroy()

    def on_cancel(self):
        self.items = None
        self.destroy()

    def show(self):
        self.wait_window()
        return self.items


class ItemTableDialog(tk.Toplevel):
    def __init__(self, parent, json_path="positions.json", preset_items=None, offset_x=150, offset_y=150):
        super().__init__(parent)
        self.parent = parent
        self.title("Ввод позиций")
        self.configure(bg=Config.BG_MAIN)
        self.transient(parent)
        self.grab_set()

        self.json_path = json_path
        self.json_data = {}
        self.set_names = []

        top_frame = tk.Frame(self, bg=Config.BG_MAIN)
        top_frame.grid(row=0, column=0, columnspan=7, sticky="ew", padx=5, pady=5)
        top_frame.grid_columnconfigure(1, weight=1)

        tk.Label(top_frame, text="Выберите набор:", bg=Config.BG_MAIN, font=("Arial", 10)).grid(row=0, column=0,
                                                                                                sticky="w")

        self.set_combo = ttk.Combobox(top_frame, state="readonly")
        self.set_combo.grid(row=0, column=1, sticky="ew", padx=5)

        load_btn = tk.Button(top_frame, text="Загрузить", command=self.load_selected_set,
                             bg=Config.BTN_BG_CALC, fg=Config.BTN_FG_CALC, font=("Arial", 10, "bold"))
        load_btn.grid(row=0, column=2, padx=5)

        edit_btn = tk.Button(top_frame, text="Редактировать набор", command=self.edit_selected_set,
                             bg=Config.BTN_BG_ADD, fg=Config.BTN_FG_ADD, font=("Arial", 10, "bold"))
        edit_btn.grid(row=0, column=3, padx=5)

        add_btn = tk.Button(top_frame, text="Добавить набор", command=self.add_new_set,
                            bg=Config.BTN_BG_ADD, fg=Config.BTN_FG_ADD, font=("Arial", 10, "bold"))
        add_btn.grid(row=0, column=4, padx=5)

        del_btn = tk.Button(top_frame, text="Удалить набор", command=self.delete_selected_set,
                            bg=Config.BTN_BG_DEL, fg=Config.BTN_FG_DEL, font=("Arial", 10, "bold"))
        del_btn.grid(row=0, column=5, padx=5)

        headers = ["№", "Артикул", "Наименование", "Количество", "Цена", "", ""]
        for col, text in enumerate(headers):
            lbl = tk.Label(self, text=text, font=("Arial", 12, "bold"), bg=Config.BG_OPTIONS_BOX)
            lbl.grid(row=1, column=col, padx=5, pady=5, sticky="ew")

        for col in range(7):
            self.grid_columnconfigure(col, weight=1)

        self.rows = []

        if preset_items and isinstance(preset_items, (list, tuple)) and len(preset_items) > 0:
            start_row = 2
            for i, item in enumerate(preset_items, start=start_row):
                new_row = ItemRow(self, i, self.add_row, self.remove_row)
                new_row.set_data(item)
                self.rows.append(new_row)
            for idx, row in enumerate(self.rows, start=start_row):
                row.update_index(idx)
        else:
            self.add_row(2)

        self.result = None

        self.apply_btn = tk.Button(self, text="Применить", command=self.on_apply,
                                   bg=Config.BTN_BG_CALC, fg=Config.BTN_FG_CALC,
                                   font=("Arial", 12, "bold"), relief="raised")
        self.apply_btn.grid(row=1000, column=0, columnspan=7, pady=10, sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.load_json()

        self.update_idletasks()
        self.set_offset_position(offset_x, offset_y)

    def set_offset_position(self, x_offset, y_offset):
        if self.parent is not None:
            try:
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
            except Exception:
                parent_x, parent_y = 0, 0
        else:
            parent_x, parent_y = 0, 0
        self.geometry(f"+{parent_x + x_offset}+{parent_y + y_offset}")

    def load_json(self):
        if not os.path.exists(self.json_path):
            messagebox.showwarning("Внимание", f"Файл {self.json_path} не найден.")
            self.json_data = {}
            self.set_names = []
            self.set_combo['values'] = []
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.json_data = json.load(f)
            self.set_names = list(self.json_data.keys())
            self.set_combo['values'] = self.set_names
            if self.set_names:
                self.set_combo.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить JSON:\n{e}")
            self.json_data = {}
            self.set_names = []
            self.set_combo['values'] = []

    def save_json(self):
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.json_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить JSON:\n{e}")

    def load_selected_set(self):
        selected = self.set_combo.get()
        if not selected:
            messagebox.showinfo("Информация", "Выберите набор из списка.")
            return
        data_list = self.json_data.get(selected, [])
        if not isinstance(data_list, list):
            messagebox.showerror("Ошибка", "Набор данных некорректен.")
            return

        while self.rows:
            row = self.rows.pop()
            row.destroy()

        start_row = 2
        for i, item in enumerate(data_list, start=start_row):
            new_row = ItemRow(self, i, self.add_row, self.remove_row)
            new_row.set_data(item)
            self.rows.append(new_row)

        if not data_list:
            self.add_row(start_row)

        for idx, row in enumerate(self.rows, start=start_row):
            row.update_index(idx)

    def edit_selected_set(self):
        selected = self.set_combo.get()
        if not selected:
            messagebox.showinfo("Информация", "Выберите набор для редактирования.")
            return
        data_list = self.json_data.get(selected, [])
        if not isinstance(data_list, list):
            messagebox.showerror("Ошибка", "Набор данных некорректен.")
            return

        dlg = EditSetDialog(self, selected, data_list.copy())
        updated_items = dlg.show()
        if updated_items is not None:
            self.json_data[selected] = updated_items
            self.save_json()
            if self.set_combo.get() == selected:
                self.load_selected_set()

    def add_new_set(self):
        new_name = simpledialog.askstring("Добавить набор", "Введите имя нового набора:", parent=self)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("Ошибка", "Имя набора не может быть пустым.")
            return
        if new_name in self.json_data:
            messagebox.showwarning("Ошибка", "Набор с таким именем уже существует.")
            return

        self.json_data[new_name] = [{"art": "", "name": "", "count": 0, "price": 0}]
        self.save_json()
        self.set_names.append(new_name)
        self.set_combo['values'] = self.set_names
        self.set_combo.set(new_name)
        self.load_selected_set()

    def delete_selected_set(self):
        selected = self.set_combo.get()
        if not selected:
            messagebox.showinfo("Информация", "Выберите набор для удаления.")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить набор '{selected}'?"):
            self.json_data.pop(selected, None)
            self.save_json()
            self.set_names.remove(selected)
            self.set_combo['values'] = self.set_names
            if self.set_names:
                self.set_combo.current(0)
                self.load_selected_set()
            else:
                while self.rows:
                    row = self.rows.pop()
                    row.destroy()

    def add_row(self, index):
        for row in self.rows:
            if row.index >= index:
                row.update_index(row.index + 1)
        new_row = ItemRow(self, index, self.add_row, self.remove_row)
        self.rows.insert(index - 2, new_row)
        for idx, row in enumerate(self.rows, start=2):
            row.update_index(idx)

    def remove_row(self, index):
        if len(self.rows) == 1:
            # Если последняя строка, не удаляем, а очищаем поля
            row = self.rows[0]
            row.clear_fields()
        else:
            for i, row in enumerate(self.rows):
                if row.index == index:
                    row.destroy()
                    self.rows.pop(i)
                    break
            for row in self.rows:
                if row.index > index:
                    row.update_index(row.index - 1)

    def on_apply(self):
        data = []
        for row in self.rows:
            item = row.get_data()
            if item["art"] or item["name"] or item["count"] or item["price"]:
                data.append(item)
        self.result = tuple(data)
        self.destroy()

    def on_close(self):
        self.result = None
        self.destroy()


def open_item_table_dialog(parent, json_path="user_positions.json", preset_items=None, offset_x=150, offset_y=150):
    dialog = ItemTableDialog(parent, json_path, preset_items, offset_x, offset_y)
    parent.wait_window(dialog)
    return dialog.result


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Главное окно")


    def open_dialog():
        preset = (
            {"art": "A-1", "name": "Стол", "count": 2, "price": 1000},
            {"art": "B-2", "name": "Стул", "count": 4, "price": 500}
        )
        result = open_item_table_dialog(root, preset_items=preset)
        if result is not None:
            print("Получен результат из диалога:")
            for item in result:
                print(item)
        else:
            print("Диалог закрыт без сохранения")


    btn = tk.Button(root, text="Открыть с пресетом", command=open_dialog)
    btn.pack(padx=20, pady=20)

    root.mainloop()
