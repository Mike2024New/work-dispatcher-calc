class CalculateResults:
    """подсчёт суммы модулей"""

    def __init__(self, moduls):
        self._moduls = moduls
        self._moduls_calculate()  # подсчёт модульных комплектующих (указание промежуточных итоговых сумм)
        self._options_calculate()  # подсчёт опциональных комплектующих

    def _moduls_calculate(self):
        for modul in self._moduls["moduls"]:
            modul_price = 0
            for key in modul:
                if isinstance(modul[key], dict) and "price" in modul[key]:
                    modul_price += modul[key]["price"]
            modul["sum_price"] = modul_price
            self._moduls["sum_price"] += modul["sum_price"] * modul["count"]

    def _options_calculate(self):
        for detail in self._moduls["options"]:
            self._moduls["sum_price"] += detail["price"] * detail["count"]
