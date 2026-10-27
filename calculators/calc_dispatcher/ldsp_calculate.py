class LdspCalculate:
    """РАСЧЁТ ДЕТАЛЕЙ ЛДСП"""

    def __init__(self, moduls, rules, table_desk_price_map, side_wall_price, ldsp_color):
        self._rules = rules  # проброс правил
        self._moduls = moduls
        self._table_desk_price_map = table_desk_price_map  # карта цен столешниц для проброса цен столешниц в ручную
        self.side_wall_price = side_wall_price
        self._ldsp_color = ldsp_color
        self._moduls_desk_calculate()  # расчёт столешниц
        self._side_panel_calculate()

    def _moduls_desk_calculate(self):
        """расчёт столешницы метр квадратный на цену из прайс-листа"""
        if all(i != 0 for i in self._table_desk_price_map):
            if any(i == 0 for i in self._table_desk_price_map):
                print(123)
                raise Exception("Если указываете цены в ручную, то нужно заполнить все модули!")
            print(len(self._table_desk_price_map))
            print(len(self._moduls["moduls"]))
            for i in range(len(self._table_desk_price_map)):
                self._moduls["moduls"][i]["desk"]["price"] = self._table_desk_price_map[i]
            return

        for i in range(len(self._moduls["moduls"])):
            length = self._moduls["moduls"][i]["desk"]["len"]
            self._moduls["moduls"][i]["desk"]["price"] = round(
                (length / 100 * self._rules["table_depth"] / 100) * self._rules["ldsp_price_area"])

    def _side_panel_calculate(self):
        """панели переезжают в опциональные комплектующие для равномерной обработки данных"""
        if self.side_wall_price:
            self._moduls["side_panel"]["price"] = self.side_wall_price
        else:
            self._moduls["side_panel"]["price"] = round(
                (self._rules["table_depth"] / 100 * self._rules["table_height"] / 100) * self._rules[
                    "ldsp_price_area"]) * 2
        self._moduls["side_panel"]["count"] = 1
        self._moduls["options"].append(self._moduls["side_panel"])
        self._moduls.pop("side_panel")  # больше панели в отдельном ключе не нужны, их можно перебросить в опции
