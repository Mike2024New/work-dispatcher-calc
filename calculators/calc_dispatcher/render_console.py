class RenderingConsole:
    def __init__(self, moduls, rules, show_price=True):
        self._rules = rules
        self._moduls = moduls
        self._show_price = show_price
        self._text = ""
        self.render_moduls()
        self.render_options()
        self.render_headers()
        self.render_notes()

    def render_moduls(self):
        for modul in self._moduls["moduls"]:
            self._text += f"\n{modul['name']}:"  # название модуля

            # если модулей более чем 1, то добавить в заголовок модулей уведомление
            if modul["count"] > 1:
                self._text += " |==>x2:"

            for key in ("table", "screen", "montage", "desk"):
                if modul[key]:  # вставка комплектующих модуля

                    self._text += f'\n{self._rules["indent_text_render"]}-{modul[key]["art"]} {modul[key]["name"]}.'
                    if self._show_price:  # если стоит галочка показывать цены в консоли
                        self._text += f'С/с: {modul[key]["price"]} руб./шт.'
            if self._show_price:  # если стоит галочка показывать цены в консоли
                self._text += f'\n{self._rules["indent_text_render"]}Итого: {modul["sum_price"]} руб./шт.'  # итоговая сумма модуля

            # если модулей более чем 1, то добавить в итоги сумму умноженную на количество
            if modul["count"] > 1 and self._show_price:
                self._text += f" |==>{modul['sum_price'] * modul['count']} руб."
            self._text += "\n"  # просто интервал строк

    def render_options(self):
        for option in self._moduls["options"]:
            self._text += f'\n-{option["art"]} {option["name"]}.'
            if self._show_price:  # если стоит галочка показывать цены в консоли
                self._text += f'С/с: {option["price"]} руб./шт.'
            if option["count"] > 1:
                if self._show_price:  # если стоит галочка показывать цены в консоли
                    self._text += f' |==>x{option["count"]}==>{option["count"] * option["price"]} руб.'
                else:
                    self._text += f' - {option["count"]} шт.'

    def render_headers(self):
        self._text = (
                self._moduls["name"] +  # итоговый заголовок
                self._text  # модульные и опциональные комплектующие
        )
        if self._show_price:
            self._text += f"\n\nИтоговая себестоимость:{self._moduls['sum_price']} руб."

    def render_notes(self):
        if "notes" in self._moduls:
            self._text += "\n\nПримечания:"
            for note in self._moduls["notes"]:
                self._text += f"\n\t-{note}"

    def show_result(self):
        print(self._text)
