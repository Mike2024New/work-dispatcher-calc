from calculators.calc_dispatcher.validators import Validators


class UserInput:
    """
    этот класс принимает на вход параметры пользователя проверяет их и переводит их в понятный БД формат
    """

    def __init__(self, tables: list, screens: list, montages: list, sockets: list, brackets: list, rules: dict,
                 ldsp_color: str, table_name: str = None, ldsp_thikness: str = None):
        """
        :type ldsp_color: object цвет столешницы и боковин
        :type ldsp_thikness: object толщина деталей из ЛДСП
        :param tables: длины столов, угловые столы на 22градуса указываются как 22, на 90 как 90, остальные по длинам
        :param screens: высоты экранов, можно передать просто пустой список
        :param montages: шины монтажные в формате  1/0 (есть или нет), можно передать пустой список
        :param sockets: [1..,2..] -> 1 - кол-во розеток на 220, 2 - кол-во rj45, можно передать пустой список
        :param brackets: [1..,2..,3..] ->кронштейны 1- малая стойка 1 монитор, 2-высокая стойка 2 монитора,
        3 - высокая стойка 1 монитор, можно передать пустой список
        :param rules: параметры расчётов, размеры столов, настройки цен и так далее.
        :param table_name: -> наименование изделия можно передать в ручную

        Пример ввода:
            table_calc = UserInput(
                tables=[22, 90, 90], # стол угловой 22 левый, угловой на 90 средний, правый прямой на 90
                screens=[45, 45], # экраны высотой 45 - 2 шт, 3 экран отсутствует, будет добавлен 0 в список (AUTO)
                montages=[1, 1], # шины монтажные, 2 шт, 3 шина отсутствует, будет добавлен 0 в список (AUTO)
                sockets=[1, 1], # розетки 1 шт, rj45 1 шт.
                brackets=[0, 0, 0] # кронштейны отсутствуют
            )
        """
        self._rules = rules  # проброс правил
        # первичная проверка введенных параметров
        Validators.validate_user_input_parametrs(tables, screens, montages, sockets, brackets)
        # 0. инициализация
        self._tables = tables  # столы задают количество модулей
        self._screens = [i for i in screens + [0] * (len(tables) - len(screens))]  # должно быть столько сколько модулей
        self._montages = [bool(i) for i in montages + [0] * (len(tables) - len(montages))]  # должн быть ст скольк мод
        self._sockets = [i for i in sockets + [0] * (3 - len(sockets))]  # этих параметров всегда 2 (розетки, rj45)
        self._brackets = [i for i in brackets + [0] * (3 - len(brackets))]  # кронштейны всегда 3 параметра
        self._ldsp_color = ldsp_color
        self._table_thikness = ldsp_thikness if ldsp_thikness else self._rules["table_desk_thikness"]
        # 1. определение динамических модулей + проверка
        self._moduls = {
            "name": table_name if table_name else "Стол диспетчера",
            "moduls": [],  # групповые модули (стол, экран, шина, столешница)
            "options": [],  # опциональные комплектующие (блоки розеток, интернет разъёмы, кронштейны для мониторов)
            'sum_price': 0  # итоговая цена за всё
        }  # вычисляемый параметр
        self.start_convert_user_input()  # запуск преобразования входного запроса пользователя

    def start_convert_user_input(self):
        """
        Корвертация пользовательского запроса и добавление необходимых комплектующих
        :return: None
        """
        self._convert_moduls()  # преобразование модульных комплектующих
        self._add_supports_for_modul()  # добавление опор промежуточных ФЛ-1701
        self._add_supports_for_screen()  # добавление стоек для экранов
        self._convert_options()  # преобразование опциональных комплектующих, жёстко прописанных по артикулам
        self._side_panel()  # добавление панелей боковых

    def _side_panel(self):
        color = self._ldsp_color if self._ldsp_color else self._rules['table_desk_color']
        self._moduls["side_panel"] = {
            "art": self._rules["side_panel_art"],
            "name": f"Комплект панелей боковых (1 кт. = 2 шт.), {color}"
        }

    def _add_supports_for_modul(self):
        """добавление опор промежуточных для составных столов если модулей несколько"""
        if len(self._moduls["moduls"]) > 1:
            self._moduls["options"].append({
                "art": "ФЛ-1701",
                "count": len(self._moduls["moduls"]) - 1
            })

    def _add_supports_for_screen(self):
        """добавление стоек крепления экранов"""
        if all(i == 0 for i in self._screens):  # экраны отсутствуют выход
            return

        # счётчик экранов
        supports = {
            self._rules["screens"][1]: 0,
            self._rules["screens"][-1]: 0
        }
        # подсчёт количества стоек (подумать как можно оптимизировать этот метод)
        for i in range(0, len(self._screens) - 1):
            # если на текущем модуле нет экрана (0), а соседний есть 45 или 85
            if self._screens[i] == 0 and self._screens[i + 1] == 45:
                supports[45] += 1
            elif self._screens[i] == 0 and self._screens[i + 1] == 85:
                supports[85] += 1
            # если на текущем модуле есть 45 экран, а соседнего нет 0 или есть 45 или есть 85
            elif self._screens[i] == 45 and self._screens[i + 1] == 0:
                supports[45] += 1
            elif self._screens[i] == 45 and self._screens[i + 1] == 85:
                supports[85] += 1
            elif self._screens[i] == 45 and self._screens[i + 1] == 45:
                supports[45] += 1
            # если на текущем модуле есть 85 экран, а соседнего нет 0 или есть 45 или есть 85
            elif self._screens[i] == 85 and self._screens[i + 1] == 0:
                supports[85] += 1
            elif self._screens[i] == 85 and self._screens[i + 1] == 45:
                supports[85] += 1
            elif self._screens[i] == 85 and self._screens[i + 1] == 85:
                supports[85] += 1

        # добавление стоек в список опциональных комплектующих
        for key in supports:
            if supports[key]:
                self._moduls["options"].append({
                    "art": f"ФЛ-1711.{key}",
                    "count": supports[key]
                })

    def _montage_len_calculate(self, key, length):
        """смещение шины монтажной на основании правил (если требуется), например на столах шина на 20 см короче"""
        montage_len = self._rules["tables"][key].get("montage_len")
        if not montage_len:
            montage_len = length - self._rules["tables"][key].get("montage_offset")
        return montage_len

    def _create_modul(self, key, length=None, height=0, is_montage=False):
        # создание модуля по ключам, работает с rules
        length = length if length else self._rules["tables"][key]["len"]
        table_color = self._ldsp_color if self._ldsp_color else self._rules["table_desk_color"]
        return {
            "table": {
                "type": key,
                "len": length,
            },
            "screen": {
                "type": key.replace("table", "screen"),
                "len": length,
                "height": height,
            },
            "montage": {
                "len": self._montage_len_calculate(key, length),
                "count": self._rules["tables"][key]["montage_count"],
                "is_montage": is_montage,
                "type": "montage"
            },
            "desk": {  # столешницы в базе не хранятся для них сразу создаётся название
                "art": "",  # пока что art пустой, потом доработаю этот момент
                "name": f'Столешница {self._rules["tables"][key]["name"]}, '  # наименование
                        f'{length}*{self._rules["table_depth"]}*{self._table_thikness}, '  # габариты
                        f'{table_color}',  # цвет
                "len": length,  # для расчёта цены в дальнейших модулях
            },
            "name": f'{self._rules["tables"][key]["modul_name"]} {length}',
        }

    def _convert_moduls(self) -> None:
        """
        Преобразователь пользовательских параметров в понятный БД тип данных. Динамические модули то есть
        прямые столы, которые имеют разные типоразмеры проверяются по правилам rules, угловые столы захардкодены
        так как они неизменны и всегда имеют заданные в методе параметры

        :return: None, добавляет модули в self.moduls
        Результат выдачи список с модулями, формата:
        [
        {
        {table:{"тип стола":..., "длина стола", ...},
        {screen:{"тип экрана":..., "длина экрана":..., "высота экрана":...}},
        {montage:{"длина шины":...,"количество шин":...,"наличие да/нет":...,}}
        },
        ]

        Пример одного модуля на выходе:
        {'table': {'type': 'table_left', 'len': 90},
        'screen': {'type': 'screen_left', 'len': 90, 'height': 45},
        'montage': {'len': 80, 'count': 1, 'is_montage': True}}
        """
        if len(self._tables) == 1:  # стол отдельностоящий (в списке модулей всего 1 модуль)
            Validators.validate_modul_table_length(check_key="table", modul_length=self._tables[0])
            self._moduls["moduls"].append(
                self._create_modul(
                    key="table",
                    length=self._tables[0],
                    height=self._screens[0],
                    is_montage=self._montages[0]
                )
            )
            return

        for i in range(len(self._tables)):
            # ПРАВЫЙ МОДУЛЬ СТОЛА (НАЧАЛЬНЫЙ)
            if i == 0:  # 1й модуль стола (он может быть либо прямым левым, либо угловым 22 длиной 120)
                if self._tables[i] == 22:  # левый угловой модуль на 22 градуса
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_angle_22_l", height=self._screens[i],
                                           is_montage=self._montages[i]))

                else:  # иначе это прямой левый модуль стола
                    Validators.validate_modul_table_length(check_key="table_left", modul_length=self._tables[i])
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_left", length=self._tables[i], height=self._screens[i],
                                           is_montage=self._montages[i]))

            # ЛЕВЫЙ МОДУЛЬ СТОЛА (КОНЕЧНЫЙ МОДУЛЬ)
            elif i == len(self._tables) - 1:  # последн мод (он может быть либо прям левым, либо угловым 22 длиной 120)

                if self._tables[i] == 22:  # правый угловой модуль на 22 градуса
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_angle_22_r", height=self._screens[i],
                                           is_montage=self._montages[i]))

                else:  # иначе это прямой правый модуль стола
                    Validators.validate_modul_table_length(check_key="table_right", modul_length=self._tables[i])
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_right", length=self._tables[i], height=self._screens[i],
                                           is_montage=self._montages[i]))

            # ЦЕНТРАЛЬНЫЕ МОДУЛИ СТОЛА
            else:  # средний модуль может быть прямой промежуточный, угловой на 90, угловой на 22
                if self._tables[i] == 22:  # промежуточный угловой на 22 градуса
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_angle_22", height=self._screens[i], is_montage=self._montages[i]))

                elif self._tables[i] == 90:  # промежуточный угловой на 90 градусов
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_angle_90", height=self._screens[i], is_montage=self._montages[i]))

                else:  # иначе это прямой промежуточный модуль стола
                    Validators.validate_modul_table_length(check_key="table_mid", modul_length=self._tables[i])
                    self._moduls["moduls"].append(
                        self._create_modul(key="table_mid", length=self._tables[i], height=self._screens[i],
                                           is_montage=self._montages[i]))

    def _convert_options(self) -> None:
        """
        Обработка опциональных не модульных комплектующих, блоки розеток, мониторы
        добавляет в self._moduls опции вида:
        [
        {"артикул":...,"количество":...},
        ]
        Пример: [{'art': 'ФЛ-1731', 'count': 1}, {'art': 'ФЛ-1733', 'count': 1}]
        Артикулы прописаны напрямую, так как они гарантированно неизменяемы
        :return:
        """
        # добавление розеток и шины заземления
        if self._sockets[0]:
            self._moduls["options"].append({"art": "ФЛ-1731", "count": self._sockets[0]})
            self._moduls["options"].append({"art": "ФЛ-1733", "count": 1})

        # добавление RJ45
        if self._sockets[1]:
            self._moduls["options"].append({"art": "ФЛ-1732", "count": self._sockets[1]})

        brackets_count = 0  # кол-во кронштейнов
        # добавление кроншнейна тип А -> низкая стойка 1 кронштейн
        if self._brackets[0]:
            self._moduls["options"].append({"art": "ФЛ-1715.45", "count": self._brackets[0]})
            brackets_count += self._brackets[0]

        # добавление кронштейна тип B -> высокая стойка 2 кронштейна
        if self._brackets[1]:
            self._moduls["options"].append({"art": "ФЛ-1715.85", "count": self._brackets[1]})
            brackets_count += self._brackets[1] * 2

        # добавление кронштейна тип C -> высокая стойка 1 кронштейн
        if self._brackets[2]:
            self._moduls["options"].append({"art": "ФЛ-1715.85", "count": self._brackets[2]})
            brackets_count += self._brackets[2]

        # кроншейны добавляются в конце, чтобы коллекция была упорядочена и были одной строкой
        if brackets_count:
            self._moduls["options"].append({"art": "ФЛ-1721", "count": brackets_count})

    def get_convert_parametrs(self):
        return self._moduls
