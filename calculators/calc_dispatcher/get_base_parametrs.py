class GetBaseParametrs:
    """
    получение параметров изделий из БД (цены, артикулы, названия и так далее)
    """

    def __init__(self, moduls: dict, base_search, rules, metall_color=None) -> None:
        """
        :param moduls: список с модулями
        :param base_search: курсор поиска в БД
        """
        self._rules = rules  # проброс правил расчёта
        self._moduls = moduls
        self._base = base_search
        self._metall_color = metall_color if metall_color else self._rules["table_metall_color"]  # цвет металла
        self._get_moduls_from_base()  # получение модульных групповых комплектующих (столы, экраны, шины монтажные)
        self._get_options_from_base()  # получение опциональных не групповых комплектующих

    def _get_modul_table_base(self, modul) -> dict:
        """
        # получение стола (обязательный модуль) / по параметрам из modul находит изделие в БД
        :param modul: тип и длина стола, например: {'type': 'table_left', 'len': 90}
        :return: артикул, название, цена, например:
        {
            'art': 'ФЛ-1107',
            'name': 'Модуль стола левый,90*100*76, RAL7047',
            'price': 0
        }
        * 'price' показан 0 в примере, чтобы не выдавать коммерческую тайну предприятия
        """
        table = self._base.get_detail_by_len_type(
            length=modul["len"],
            detail_type=modul["type"]
        )
        if not table:
            # при использовании UserInput возникновение этого исключения маловероятно
            raise Exception(f'В базе нет модуля с параметрами {modul}')
        return {
            "art": table[0][0],
            "name": f'{table[0][1]},'  # название
                    f'{modul["len"]}*{self._rules["table_depth"]}*{self._rules["table_height"]}, '  # габариты
                    f'{self._metall_color}',  # цвет
            "price": table[0][-1],
        }

    def _get_modul_screen_base(self, modul) -> dict:
        """
        Получение экрана из БД.
        :param modul: тип/длина/высота, например:{'type': 'screen_left', 'len': 90, 'height': 45}
        :return: словарь с артикулом, наименованием и ценой, или {} если высота экрана 0 (то есть отсутствует)
        например:
        {
            'art': 'ФЛ-1607.45',
            'name': 'Экран настольный модуля левый 90 h=45 см. RAL7047',
            'price': 0
        }
        *'price' показан 0 в примере, чтобы не выдавать коммерческую тайну предприятия
        """
        # если высота экрана 0, то экран не нужен, вернуть None
        if not modul["height"]:
            return {}
        screen = self._base.get_detail_by_height_len_type(
            height=modul["height"],
            length=modul["len"],
            detail_type=modul["type"]
        )
        if not screen:
            # при использовании UserInput возникновение этого исключения маловероятно
            raise Exception(f'В базе нет модуля с параметрами {modul}')

        return {
            "art": screen[0][0],
            "name": f'{screen[0][1]} '  # название
                    f'{modul["len"]} h={modul["height"]} см. '  # габарит по длине и высота
                    f'{self._metall_color}',  # цвет
            "price": screen[0][-1],
        }

    def _get_modul_montage_base(self, modul):
        """
        Поиск шин монтажных в БД и возвращение их
        :param modul: длина/кол-во/наличие/тип например: {'len': 80, 'count': 1, 'is_montage': True, 'type': 'montage'}
        :return: словарь с полученными из БД параметрами:
        'montage': {
            'art': 'ФЛ-1903',
            'name': 'Шина монтажная L=70 см',
            'price': 0,
            'count': 2
        }
        * 'price' показан 0 в примере, чтобы не выдавать коммерческую тайну предприятия
        """
        if not modul["is_montage"]:
            return {}
        montage = self._base.get_detail_by_len_type(length=modul["len"], detail_type=modul["type"])
        if not montage:
            # при использовании UserInput возникновение этого исключения маловероятно
            raise Exception(f'В базе нет модуля с параметрами {modul}')
        return {
            "art": montage[0][0],
            "name": f"{montage[0][1]} L={modul['len']} см",
            "price": montage[0][-1],
            "count": modul["count"]  # для шин важно количество
        }

    def _get_moduls_from_base(self):
        """получение модульных комплектующих из БД"""
        for i in range(len(self._moduls["moduls"])):
            # получение модуля
            self._moduls["moduls"][i]["table"] = self._get_modul_table_base(modul=self._moduls["moduls"][i]["table"])
            # получение экрана
            self._moduls["moduls"][i]["screen"] = self._get_modul_screen_base(modul=self._moduls["moduls"][i]["screen"])
            # получение шины монтажной
            self._moduls["moduls"][i]["montage"] = self._get_modul_montage_base(
                modul=self._moduls["moduls"][i]["montage"])

    def _get_options_from_base(self):
        """получение опциональных комплектующих из БД"""
        for i in range(len(self._moduls["options"])):
            # print(self._moduls["options"][i])
            # input()
            data = self._base.get_detail_by_art(art=self._moduls["options"][i]["art"])
            if not data:
                # при использовании UserInput возникновение этого исключения маловероятно
                raise Exception(f'не найден товар {self._moduls["options"][i]["art"]} в БД')
            self._moduls["options"][i] = {
                "art": data[0][0],
                "name": data[0][1],
                "price": data[0][-1],
                "count": self._moduls["options"][i]["count"]
            }

    def get_convert_parametrs(self):
        return self._moduls
