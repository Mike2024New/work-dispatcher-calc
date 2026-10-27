import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from calculators.calc_dispatcher.base.base_manager import BaseDispatcherSearch
from calculators.calc_dispatcher.main import DispatcherCalcManager
from utilits.ui_configurator import start as edit_config_start
from utilits.work_json import read_json_file, rec_json_file


# Класс конфигурации: здесь хранятся все цвета, шрифты и размеры для удобства настройки внешнего вида
class Config:
    # Цвета
    BG_MAIN = "#ffffff"  # Основной фон окна приложения
    BG_MODULES = "#e6e6e6"  # Фон блоков с модулями и опциями
    BG_OPTIONS_BOX = "#e6e6e6"  # Фон блока опций (без рамки)
    BTN_BG_CALC = "black"  # Цвет фона кнопки "Расчёт"
    BTN_FG_CALC = "white"  # Цвет текста кнопки "Расчёт"
    BTN_BG_CLEAR = "#555555"  # Цвет фона кнопки "Очистить"
    BTN_FG_CLEAR = "white"  # Цвет текста кнопки "Очистить"
    BTN_BG_ADD = "black"  # Цвет фона кнопок "+" для добавления модуля
    BTN_FG_ADD = "white"  # Цвет текста кнопок "+"
    BTN_BG_DEL = "red"  # Цвет фона кнопок "-" для удаления модуля
    BTN_FG_DEL = "white"  # Цвет текста кнопок "-"
    LABEL_NUM_FG = "red"  # Цвет номера модуля (красный)

    # Шрифты
    FONT_HEADER = ("Arial", 16, "bold")  # Шрифт заголовков "МОДУЛИ" и "Опции"
    FONT_MODULE_NUM = ("Arial", 13, "bold")  # Шрифт номера модуля
    FONT_MODULE_TEXT = ("Arial", 10)  # Шрифт текста внутри модулей (радиокнопки, чекбоксы)
    FONT_BUTTON = ("Arial", 12, "bold")  # Шрифт кнопок "+" и "-"
    FONT_CALC_BUTTON = ("Arial", 8, "bold")  # Шрифт кнопок "Расчёт" и "Очистить"
    FONT_OPTION_LABEL = ("Arial", 10)  # Шрифт меток в блоке опций
    FONT_OPTION_SPINBOX = ("Arial", 10)  # Шрифт спинбоксов в блоке опций

    # Размеры кнопок и элементов
    BTN_WIDTH_SMALL = 2
    BTN_HEIGHT_SMALL = 1
    BTN_WIDTH_CALC = 15
    BTN_HEIGHT_CALC = 2
    COMBOBOX_WIDTH = 45
    OPTION_LABEL_WIDTH = 26


class ModuleListForSelect:
    def __init__(self, directory: Path):
        self.directory = directory
        self.bs = BaseDispatcherSearch(directory=self.directory / 'base')

    # получение списка модулей из БД
    def _get_moduls_from_base(self, filters_type, like=True):
        res = []
        for filtr in filters_type:
            answer = self.bs.get_list_details_by_type(type_detail=filtr, like=like)
            res += [f"{answer[i][0]} {answer[i][1]} {answer[i][2]}" for i in range(len(answer))]
        return res

    # получение списка модулей в зависимости от условий
    def get_moduls_list(self, number):
        if number == 0:
            res = self._get_moduls_from_base(
                filters_type=("table", "table_left", "table_angle_22_l"),
                like=False
            )
            res.insert(0, "Выберите модуль")
            return res
        else:
            res = self._get_moduls_from_base(
                filters_type=(
                    "table_mid",
                    "table_angle_90",
                    "table_angle_22",
                    "table_angle_22_r",
                    "table_right",
                ),
                like=False
            )
            res.insert(0, "Выберите модуль")
            return res


# Класс, описывающий один блок модуля с настройками
class ModuleFrame(tk.Frame):
    def __init__(self, master, idx, insert_callback, remove_callback, module_list):
        # Инициализация фрейма модуля с серым фоном
        super().__init__(master, bg=Config.BG_MODULES)
        self.module_list = module_list
        self.insert_callback = insert_callback  # Функция для добавления модуля после текущего
        self.remove_callback = remove_callback  # Функция для удаления текущего модуля
        self.idx = idx  # Номер модуля (для отображения)

        # Метка с номером модуля (красным цветом)
        self.num_label = tk.Label(self, text=str(idx), font=Config.FONT_MODULE_NUM,
                                  fg=Config.LABEL_NUM_FG, bg=Config.BG_MODULES, width=2)
        self.num_label.grid(row=0, column=0, padx=(5, 8), sticky="w")

        # Комбобокс для выбора модуля
        self.selected_option = tk.StringVar(value=self.module_list[0])
        self.combo = ttk.Combobox(self, values=self.module_list, textvariable=self.selected_option,
                                  state="readonly", width=Config.COMBOBOX_WIDTH)
        self.combo.grid(row=0, column=1, padx=2, sticky="ew")

        # Радиокнопки для выбора угла экрана
        self.screen_var = tk.IntVar(value=0)
        rb_frame = tk.Frame(self, bg=Config.BG_MODULES)
        rb_frame.grid(row=0, column=2, padx=8)
        tk.Radiobutton(rb_frame, text="0", variable=self.screen_var, value=0,
                       bg=Config.BG_MODULES, font=Config.FONT_MODULE_TEXT).pack(side="left", padx=2)
        tk.Radiobutton(rb_frame, text="45", variable=self.screen_var, value=45,
                       bg=Config.BG_MODULES, font=Config.FONT_MODULE_TEXT).pack(side="left", padx=2)
        tk.Radiobutton(rb_frame, text="85", variable=self.screen_var, value=85,
                       bg=Config.BG_MODULES, font=Config.FONT_MODULE_TEXT).pack(side="left", padx=2)

        # Чекбокс "шина монтажная"
        self.montage_var = tk.BooleanVar()
        self.montage_cb = tk.Checkbutton(self, text="шина монтажная", variable=self.montage_var,
                                         bg=Config.BG_MODULES, font=Config.FONT_MODULE_TEXT)
        self.montage_cb.grid(row=0, column=3, padx=(10, 2))

        # ===== NEW ===================
        # Добавление поля для ввода цены за столешницу в ручную
        # self.table_desk_price_var = tk.IntVar()
        # self.table_desk_price = tk.Entry(self, textvariable=self.table_desk_price_var)
        # self.table_desk_price.grid(row=0, column=4, padx=(10, 2))

        # добавляем строку с переопределением стоимости столешницы
        self.table_desk_price_var = tk.IntVar()
        self.table_desk_price = tk.Spinbox(
            self, textvariable=self.table_desk_price_var,
            font=Config.FONT_OPTION_SPINBOX,
            from_=0,
            width=10
        )
        self.table_desk_price.grid(row=0, column=4, padx=(10, 2))

        # ===== NEW ===================

        # Кнопка добавления нового модуля после текущего
        self.add_btn = tk.Button(self, text="+", command=self.insert_after,
                                 bg=Config.BTN_BG_ADD, fg=Config.BTN_FG_ADD,
                                 width=Config.BTN_WIDTH_SMALL, height=Config.BTN_HEIGHT_SMALL,
                                 font=Config.FONT_BUTTON, bd=0)
        self.add_btn.grid(row=0, column=5, padx=(8, 2))

        # Кнопка удаления текущего модуля
        self.del_btn = tk.Button(self, text="-", command=self.remove_self,
                                 bg=Config.BTN_BG_DEL, fg=Config.BTN_FG_DEL,
                                 width=Config.BTN_WIDTH_SMALL, height=Config.BTN_HEIGHT_SMALL,
                                 font=Config.FONT_BUTTON, bd=0)
        self.del_btn.grid(row=0, column=6, padx=(2, 8))

        # Позволяет комбобоксу растягиваться по ширине
        self.grid_columnconfigure(1, weight=1)

    # Вызов функции добавления модуля после текущего
    def insert_after(self):
        self.insert_callback(self)

    # Вызов функции удаления текущего модуля
    def remove_self(self):
        self.remove_callback(self)

    # Обновление номера модуля (например, после удаления/добавления)
    def set_number(self, num):
        if self.num_label.winfo_exists():
            self.num_label.config(text=str(num))

    # Получение данных из модуля для расчёта
    def get_data(self):
        return {
            "module": self.selected_option.get(),
            "screen": self.screen_var.get(),
            "montage": self.montage_var.get(),
            "desk_price": self.table_desk_price_var.get()
        }

    # Метод сброса параметров модуля к значениям по умолчанию
    def reset_to_default(self):
        self.selected_option.set(self.module_list[0])  # "Выберите модуль"
        self.screen_var.set(0)  # Радиокнопка "0"
        self.montage_var.set(False)  # Снимаем галочку "шина монтажная"


# Основное приложение
class ModulesApp(tk.Tk):
    def __init__(self, directory: Path):
        super().__init__()
        self.user_positions = []  # пользовательские позиции
        self.option_data = read_json_file(file_path=directory / 'ui_parametrs.json')
        self.option_parametrs = [
            ("Розетки (ФЛ-1731):", "sockets", "num", 0),
            ("Патч панели RJ-45 (ФЛ-1732):", "patch_panels", "num", 0),
            ("Стойка низкая 1 монитор:", "stand_low_1", "num", 0),
            ("Стойка высокая 2 монитора:", "stand_high_2", "num", 0),
            ("Стойка высокая 1 монитор:", "stand_high_2b", "num", 0),
            ("Боковины стоимость:", "side_wall_price", "num", 0),
            ("Толщина лдсп: (текущий)", "ldsp_thikness", "float", self.option_data['ldsp_thikness_default']['value']),
            ("ЛДСП цвет (текущий):", "ldsp_color", "txt", self.option_data['ldsp_name_decor_default']['value']),
            ("Металл цвет (текущий):", "metal_color", "txt", self.option_data['metall_name_decor_default']['value']),
        ]

        self.title("Модули и опции")  # Заголовок окна
        self.geometry("1300x520")  # Размер окна
        self.configure(bg=Config.BG_MAIN)  # Основной фон окна
        self.modules_area = None
        self.module_frames = None
        self.options_vars = None
        self.calc_btn = None
        self.clear_btn = None
        self.directory = directory
        self.initialize()
        file_path = Path(self.directory / 'ui_notes.json')
        self.notes_list = read_json_file(file_path=file_path)['notes']

    def initialize(self):
        # Контейнер для левой и правой части, с отступами
        container = tk.Frame(self, bg=Config.BG_MAIN)
        container.pack(fill="both", expand=True, padx=8, pady=8)
        container.grid_rowconfigure(0, weight=1)  # Растяжение по вертикали
        container.grid_columnconfigure(0, weight=4)  # Левая часть шире
        container.grid_columnconfigure(1, weight=1)  # Правая часть уже

        # Левая часть: блок с модулями
        left_frame = tk.Frame(container, bg=Config.BG_MODULES)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        left_frame.grid_rowconfigure(1, weight=1)  # Растяжение области модулей
        left_frame.grid_columnconfigure(0, weight=1)

        # Заголовок "МОДУЛИ"
        tk.Label(left_frame, text="МОДУЛИ:", font=Config.FONT_HEADER, bg=Config.BG_MODULES) \
            .grid(row=0, column=0, sticky="w", pady=(16, 8), padx=16)

        # Область для размещения модулей
        self.modules_area = tk.Frame(left_frame, bg=Config.BG_MODULES)
        self.modules_area.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.module_frames = []
        self.add_module(-1)  # Добавляем первый модуль по умолчанию

        # Сразу сбрасываем первый модуль к значениям по умолчанию
        self.module_frames[0].reset_to_default()

        # Правая часть: блок с опциями и кнопками
        right_frame = tk.Frame(container, bg=Config.BG_MODULES)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        right_frame.grid_rowconfigure(1, weight=1)  # Растяжение области опций
        right_frame.grid_columnconfigure(0, weight=1)

        # Заголовок "Опции"
        tk.Label(right_frame, text="Опции:", font=Config.FONT_HEADER, bg=Config.BG_MODULES) \
            .grid(row=0, column=0, sticky="w", pady=(16, 8), padx=16)

        # Блок опций (без рамки, серый фон)
        options_box = tk.Frame(right_frame, bg=Config.BG_OPTIONS_BOX, bd=0, relief="flat", padx=8, pady=8)
        options_box.grid(row=1, column=0, sticky="n", padx=16)

        # Словарь для хранения переменных опций
        self.options_vars = {}
        for i, (label, key, type_input, value) in enumerate(self.option_parametrs):
            tk.Label(options_box, text=label, bg=Config.BG_OPTIONS_BOX, anchor="w",
                     width=Config.OPTION_LABEL_WIDTH, font=Config.FONT_OPTION_LABEL) \
                .grid(row=i, column=0, sticky="w", padx=0, pady=2)

            # целочисленные типы данных
            if type_input == "num":
                var = tk.IntVar(value=value)
                spin = tk.Spinbox(options_box, from_=0, to=99, width=5, textvariable=var,
                                  font=Config.FONT_OPTION_SPINBOX)
                spin.grid(row=i, column=1, padx=0, pady=2, sticky='e')
                self.options_vars[key] = var

            # тип данных дробные числа
            elif type_input == "float":
                var = tk.DoubleVar(value=value)
                spin = tk.Spinbox(options_box, from_=0, to=99, width=5, textvariable=var,
                                  font=Config.FONT_OPTION_SPINBOX, increment=0.1)
                spin.grid(row=i, column=1, padx=0, pady=2, sticky='e')
                self.options_vars[key] = var

            # тип данных строка обрабатываем это
            elif type_input == "txt":
                var = tk.StringVar(value=value)
                text_inp = tk.Entry(options_box, width=20, textvariable=var, font=Config.FONT_OPTION_SPINBOX)
                text_inp.grid(row=i, column=1, padx=0, pady=0, sticky='e')
                self.options_vars[key] = var

        # Контейнер для кнопок "Расчёт" и "Очистить"
        buttons_frame = tk.Frame(right_frame, bg=Config.BG_MODULES)
        buttons_frame.grid(row=2, column=0, sticky="se", padx=(0, 30), pady=(8, 18))

        buttons = [
            ("Расчёт", self.calculate, Config.BTN_BG_CALC, Config.BTN_FG_CALC),
            ("Доп позиции", self.add_user_positions, Config.BTN_BG_CALC, Config.BTN_FG_CALC),
            ("Конфигурация", self.config_window, Config.BTN_BG_CALC, Config.BTN_FG_CALC),
            ("Прайс", self.update_price, Config.BTN_BG_CALC, Config.BTN_FG_CALC),
            ("Примечания", self.update_notes, Config.BTN_BG_CALC, Config.BTN_FG_CALC),
            ("Очистить", self.clear_all, Config.BTN_BG_CLEAR, Config.BTN_FG_CLEAR)
        ]

        for i, (text, cmd, bg, fg) in enumerate(buttons):
            btn = tk.Button(buttons_frame, text=text, font=Config.FONT_CALC_BUTTON,
                            bg=bg, fg=fg,
                            width=Config.BTN_WIDTH_CALC, height=Config.BTN_HEIGHT_CALC,
                            command=cmd, bd=0)
            row = i // 2  # номер строки (каждые 2 кнопки новая строка)
            col = i % 2  # номер столбца (0 или 1)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # Чтобы кнопки растягивались по ширине колонок (опционально)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

    def add_user_positions(self):
        from calculators.calc_dispatcher.ui_add_user_position import open_item_table_dialog
        user_positions = open_item_table_dialog(
            self,
            json_path=os.path.join(self.directory, 'user_positions.json'),
            preset_items=self.user_positions,
        )
        if user_positions:
            self.user_positions = [pos for pos in user_positions if pos["count"] > 0]
            for i in range(len(self.user_positions)):
                if isinstance(self.user_positions[i]['price'], float):
                    self.user_positions[i]['price'] = int(self.user_positions[i]['price'])
        else:
            self.user_positions = None

    def update_notes(self):
        from calculators.calc_dispatcher.ui_notes_edit import edit_notes
        file_path = self.directory / 'ui_notes.json'
        self.notes_list = read_json_file(
            file_path=file_path
        )['notes']
        updated_notes = edit_notes(self.notes_list)
        if updated_notes is not None:
            updated_notes = [note for note in updated_notes if note.strip() != ""]
            rec_json_file(
                file_path=file_path,
                data={"notes": updated_notes}
            )
            messagebox.showinfo(
                "Успешно",
                "Готово, перезапустите приложение, чтобы изменения вступили в силу."
            )

    def update_price(self):
        from calculators.calc_dispatcher.ui_price_update import start as update_price
        disp_manager = DispatcherCalcManager(directory=self.directory)
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
        update_price(
            directory=self.directory / 'base' / 'price',
            txt=txt,
            callback=disp_manager.update_price_ui
        )

    def config_window(self):
        edit_config_start(
            configure_json_path=self.directory / "ui_parametrs.json"
        )

    # Добавление нового модуля в список и обновление отображения
    def add_module(self, idx):
        modules_data = [m.get_data() for m in self.module_frames]
        if modules_data and "ФЛ" not in modules_data[0]['module']:
            messagebox.showinfo(
                "error",
                "Нужно выбрать хотябы один стол, чтобы двигаться дальше"
            )
            return
        if modules_data and any(f"ФЛ-100{num}" in modules_data[-1]['module'] for num in range(1, 9)):
            messagebox.showinfo(
                "error",
                "После стола отдельностоящего модули добавлять нельзя, для продления выберите левый модуль"
            )
            return
        if modules_data and "правый" in modules_data[-1]['module']:
            messagebox.showinfo(
                "error",
                "После правого модуля нельзя добавлять следующие модули, выберите промежуточные модули"
            )
            return

        module = ModuleFrame(
            self.modules_area,
            idx + 1,
            self.insert_module_after,
            self.remove_module,
            # ниже передаём список модулей который будет доступен в опциях
            module_list=ModuleListForSelect(directory=self.directory).get_moduls_list(number=idx + 1)
        )
        self.module_frames.insert(idx + 1, module)
        self.redraw_modules()

    # Вставка нового модуля после указанного
    def insert_module_after(self, module):
        idx = self.module_frames.index(module)
        self.add_module(idx)

    # Удаление модуля из списка и обновление отображения
    def remove_module(self, module):
        if len(self.module_frames) > 1:  # Минимум один модуль должен оставаться
            module.destroy()
            self.module_frames.remove(module)
            self.redraw_modules()

    # Обновление списка модулей на экране и перенумерация
    def redraw_modules(self):
        for widget in self.modules_area.winfo_children():
            widget.pack_forget()
        for idx, module in enumerate(self.module_frames):
            module.set_number(idx + 1)
            module.pack(fill="x", pady=6)

    # Обработка нажатия кнопки "Расчёт" - выводит данные в информационном окне
    def calculate(self):
        # from calculators.calc_dispatcher.ui_add_user_position import open_item_table_dialog
        modules_data = [m.get_data() for m in self.module_frames]
        options_data = {k: v.get() for k, v in self.options_vars.items()}
        tables = []
        screens = []
        montages = []
        desk_price_map = []
        count = 1
        # print(self.user_positions)

        for i in range(len(modules_data)):
            if "90º" in modules_data[i]['module']:
                modules_data[i]['module'] = modules_data[i]['module'] + " " + "90"
            elif "22.5º" in modules_data[i]['module']:
                modules_data[i]['module'] = modules_data[i]['module'] + " " + "22"

            # print(modules_data[i])

        for data in modules_data:
            if not data["module"].split()[-1].isdigit():
                messagebox.showinfo("error", f"Не выбран модуль № {count}, выберите стол.")  # модуль не выбран, выходим
                return
            tables.append(int(data["module"].split()[-1]))
            screens.append(int(data["screen"]))
            montages.append(int(data["montage"]))
            desk_price_map.append(int(data["desk_price"]))
            count += 1

        try:
            # user_positions = open_item_table_dialog(self, json_path=os.path.join(self.directory, 'user_positions.json'))
            # user_positions = tuple([pos for pos in user_positions if pos["count"] > 0])
            disp_manager = DispatcherCalcManager(self.directory)

            if self.user_positions:
                for i in range(len(self.user_positions)):
                    self.user_positions[i]['name'] += options_data['ldsp_color']

            disp_manager.calculate(
                tables=tables,
                screens=screens,
                montages=montages,
                sockets=[options_data['sockets'], options_data['patch_panels']],
                brackets=[options_data['stand_low_1'], options_data['stand_high_2'], options_data['stand_high_2b']],
                show_price=True,
                ldsp_price_area=self.option_data["ldsp_price_area"]["value"],
                ldsp_color=options_data['ldsp_color'],
                ldsp_thikness=options_data['ldsp_thikness'],
                metal_color=options_data['metal_color'],
                side_wall_price=options_data["side_wall_price"],
                table_desk_price_map=desk_price_map,
                show_result_html=self.option_data['show_result_html']['value'],
                notes=self.notes_list,
                user_postions=self.user_positions if self.user_positions else (),  # пользовательские позиции если есть
            )
        except Exception as err:  # пробрасываем ошибки посланные бизнес логикой и выводим их в msg box
            messagebox.showinfo("error bisnes logic", f"{err}")
            raise

            # Обработка нажатия кнопки "Очистить" - сбрасывает все модули кроме первого и обнуляет опции

    def clear_all(self):
        # Удаляем все модули, кроме первого
        while len(self.module_frames) > 1:
            module = self.module_frames[-1]
            module.destroy()
            self.module_frames.pop()
        self.redraw_modules()

        # Сбрасываем первый модуль к значениям по умолчанию
        if self.module_frames:
            self.module_frames[0].reset_to_default()

        # Сбрасываем все параметры в опциях в 0
        for var in self.options_vars.values():
            var.set(0)


def start_app(directory: Path):
    """
    Запуск ui версии приложения
    :param directory: пример пути (для этого проекта): os.path.join(os.getcwd(), 'calculators', 'calc_dispatcher' )
    :return: запуск окна приложения
    """
    ModulesApp(directory=directory).mainloop()  # запускаем приложение из внешних модулей


# Запуск приложения
if __name__ == "__main__":
    from infrastructure_path_utils import get_root_dir_path

    root_dir = get_root_dir_path() / "calculators" / "calc_dispatcher"
    app2 = ModulesApp(directory=root_dir)
    app2.mainloop()
