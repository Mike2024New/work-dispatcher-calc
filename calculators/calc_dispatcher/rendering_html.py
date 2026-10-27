import os


def format_price(number: int) -> str:
    return f"{number:,}".replace(",", " ")


class FileHtml:
    """
    Вставка результата в html с учётом разделителей
    (метод универсальный) работает на базе разделителей:
    <!--INSERT-->
    <!--/INSERT-->
    """

    @classmethod
    def start(cls, directory, data, open_file=True):
        file_html = os.path.join(directory, 'result', 'result_html.html')
        res = cls._open_html(file_html_path=file_html)
        left = res.split("<!--INSERT-->")[0]
        right = res.split("<!--/INSERT-->")[-1]
        res = left + "<!--INSERT-->\n" + data + "\n<!--/INSERT-->" + right
        cls._save_html(file_html_path=file_html, data=res)
        if open_file:
            os.startfile(file_html)

    @staticmethod
    def _open_html(file_html_path):
        with open(file=file_html_path, mode='r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _save_html(file_html_path, data):
        with open(file=file_html_path, mode='w', encoding='utf-8') as f:
            f.write(data)


class RenderingHtml:
    def __init__(self, moduls, rules, show_price=True, directory=1):
        self._moduls = moduls  # отображение модулей
        self._directory = directory
        self._rules = rules
        self._show_price = show_price
        self._text = ""
        self._start()

    def _start(self):
        self._render_name()  # название модуля
        self._render_moduls()  # ветка рендеринга модульных (групповых) комплектующих
        self._render_options()  # ветка рендеринга опциональных комплектующих (общие комплектующие)
        if self._show_price:
            self._render_result()  # итоговая себестоимость
        self._render_notes()  # ветка рендеринга примечаний

    def _render_notes(self):
        if "notes" in self._moduls:  # на случай если примечания не указаны
            header = self._render_html("Примечания:", tag="h2", new_str=False)
            notes = ""
            i = 1
            for note in self._moduls["notes"]:
                notes += self._render_html(f"{i}.{note}", tag="li", new_str=False)
                i += 1
            notes = self._render_html(notes, tag='ul', new_str=True)
            self._text += "\n" + self._render_html(header + notes, tag='div', class_name='block', new_str=True)

    def _render_result(self):
        """
        :return:
        """
        result = f"Итоговая себестоимость: "
        result += self._render_html(format_price(self._moduls["sum_price"]), tag="span", class_name="price-result")
        result += " руб."
        result = self._render_html(result, tag="h2")
        self._text += "\n" + self._render_html(result, tag='div', class_name='block', new_str=True)

    def _render_name(self):
        """
        Наименование расчёта изделия
        :return:
        """
        self._text += self._render_html(self._moduls['name'], tag='h1', class_name='block-header') + "\n\n"

    def _render_options(self):
        block = ""
        for option in self._moduls["options"]:
            block += self._render_row(option) + "\n"
        block = self._render_html(block, tag='ul', new_str=True)
        self._text += self._render_html(block, tag='div', class_name='block', new_str=True)

    def _render_moduls(self):
        """
        Обход модульных комплектующих / записывает полученные результаты в self._text который записывается в hmtl
        :return:
        """
        for modul in self._moduls["moduls"]:
            self._text += "\n\n" + self._render_one_modul(modul)

    def _render_one_modul(self, modul):
        """
        :param modul: один модуль имеющий тип {"table":..., "screen":..., "montage":..., "desk":...}
        Внутри каждого типа должен быть вложенный класс имеющий структуру формата:
        'table': {'art': ..., 'name': ..., 'price': ..., "count": ...} то есть базовый тип обрабатываемый
        в render_row
        :return: модуль в формате html
        """
        header = modul["name"]
        plural_modul = ""
        if modul["count"] > 1:
            plural_modul = self._render_html(f"|==>x{modul['count']}", tag='span', class_name='header-price')

        header = self._render_html(f"{header}{plural_modul}:", tag="h2")
        rows = "\n".join([self._render_row(modul[key]) for key in ("table", "screen", "montage", "desk") if modul[key]])
        rows = self._render_html(rows, tag="ul", new_str=True)

        if self._show_price:
            result_price = self._render_html(format_price(modul['sum_price']), tag="span", class_name="price")
            result_string = f"Итого: {result_price} руб./модуль."
            if modul["count"] > 1:
                result_string += self._render_html(f" |==>{format_price(modul['sum_price'] * modul['count'])} руб.",
                                                   tag='span',
                                                   class_name='price')
            result_string = self._render_html(result_string, tag="h3")
            return self._render_html(string=header + rows + result_string, tag="div", class_name="block",
                                     new_str=True)
        return self._render_html(string=header + rows, tag="div", class_name="block",
                                 new_str=True)

    def _render_row(self, detail) -> str:
        """
        Ядро класса, базовый случай рендеринг одной позиции имеющей структуру:
        {'art':..., 'name':..., 'price':..., 'count':...}
        :param detail: входная деталь
        :return: html строка с заданными правилами
        """
        # формируем базовую строку
        art = self._render_html(detail['art'], tag="span", class_name="art")
        name = detail['name']
        row = f"{art} {name}."

        # здесь добавляется цена в строку если она указана в требованиях show_price
        if self._show_price:
            price = self._render_html(format_price(detail['price']), tag="span", class_name="price")
            row += f"С/с: {price} руб./шт."
        if "count" in detail and detail["count"] > 1:
            mul = self._render_html(f"x{detail['count']}", tag="span", class_name="price")
            price_plural = f" ==> {mul}" if detail['count'] else ""
            row += price_plural
            if self._show_price:  # возможность не указывать цены
                price_many = self._render_html(format_price(detail['count'] * detail['price']), tag="span",
                                               class_name="price")
                row += f" ==> {price_many} руб."
        return self._render_html(string=row, tag="li")

    def get_text(self):
        return self._text

    def show_result(self):
        FileHtml.start(data=self.get_text(), open_file=True, directory=self._directory)

    @staticmethod
    def _render_html(string, tag, class_name="", new_str=False):
        """
        функция добавляет html теги и классы к заданной строке
        :param string:  строка
        :param tag: тег (без скобок)
        :param class_name: класс (если есть)
        :param new_str:  перенос на новую строку
        :return: строку с тегами и классом если указан
        """
        class_name = f" class='{class_name}'" if class_name else ""
        new_str = "\n" if new_str else ""
        return f"<{tag}{class_name}>{new_str}{string}{new_str}</{tag}>"


if __name__ == '__main__':
    # цены убраны чтобы не выдавать финансовую тайну
    test_modul = {'name': 'Стол диспетчера', 'moduls': [
        {'table': {'art': 'ФЛ-1115', 'name': 'Модуль стола левый,130*100*76, RAL7047', 'price': 0},
         'screen': {'art': 'ФЛ-1615.85', 'name': 'Экран настольный модуля левый 130 h=85 см. RAL7047', 'price': 0},
         'montage': {'art': 'ФЛ-1908', 'name': 'Шина монтажная L=120 см', 'price': 0, 'count': 1},
         'desk': {'art': '', 'name': 'Столешница модуля левого, 130*100*3.2, Арктика серый', 'len': 130,
                  'price': 0}, 'name': 'модуль стола для диспетчера левый 130', 'count': 1, 'sum_price': 0},
        {'table': {'art': 'ФЛ-1151', 'name': 'Модуль стола промежуточный,100*100*76, RAL7047', 'price': 0},
         'screen': {'art': 'ФЛ-1651.85', 'name': 'Экран настольный модуля промежуточный 100 h=85 см. RAL7047',
                    'price': 0},
         'montage': {'art': 'ФЛ-1906', 'name': 'Шина монтажная L=100 см', 'price': 0, 'count': 1},
         'desk': {'art': '', 'name': 'Столешница модуля промежуточного, 100*100*3.2, Арктика серый', 'len': 100,
                  'price': 0}, 'name': 'модуль стола для диспетчера промежуточный 100', 'count': 2,
         'sum_price': 0},
        {'table': {'art': 'ФЛ-1104', 'name': 'Модуль стола правый,70*100*76, RAL7047', 'price': 0}, 'screen': {},
         'montage': {},
         'desk': {'art': '', 'name': 'Столешница модуля правого, 70*100*3.2, Арктика серый', 'len': 70, 'price': 0},
         'name': 'модуль стола для диспетчера правый 70', 'count': 1, 'sum_price': 0}],
                  'options': [{'art': 'ФЛ-1701', 'name': 'Опора модуля промежуточная', 'price': 0, 'count': 3},
                              {'art': 'ФЛ-1711.85', 'name': 'Стойка экрана промежуточная', 'price': 0, 'count': 3},
                              {'art': 'ФЛ-1715.85', 'name': 'Стойка кронштейна под монитор', 'price': 0, 'count': 3},
                              {'art': 'ФЛ-1721', 'name': 'Кронштейн под монитор', 'price': 0, 'count': 6},
                              {'art': 'ФЛ-091', 'name': 'Комплект панелей боковых (1 кт. = 2 шт.), Арктика серый',
                               'price': 0, 'count': 1}], 'sum_price': 0,
                  "notes": [
                      "Максимальный вес монитора 8 кг.",
                      "Внутренняя глубина технического отсека 350 мм."
                  ]
                  }

    result_in_method = RenderingHtml(moduls=test_modul, rules=None, show_price=False)
    FileHtml.start(data=result_in_method.get_text(), open_file=True, directory=os.path.join(os.getcwd()))
