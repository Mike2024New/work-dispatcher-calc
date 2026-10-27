import os
# модуль для обновления прайса:
from calculators.calc_dispatcher.base.base_manager import BaseDispatcherUpdate, BaseDispatcherSearch
# правила расчёта (можно переопределять здесь):
from calculators.calc_dispatcher.rules import rules
# модули для расчёта мебели:
from calculators.calc_dispatcher.user_input import UserInput  # перевод пользовательского ввода в формат понятный sql
from calculators.calc_dispatcher.get_base_parametrs import \
    GetBaseParametrs  # получение модулей и комплектующих из БД sql
from calculators.calc_dispatcher.moduls_counter import \
    ModulsCounter  # удаление дублей модулей с указанием их количества
from calculators.calc_dispatcher.ldsp_calculate import LdspCalculate  # расчёт деталей из ЛДСП
from calculators.calc_dispatcher.add_user_postions import AddUserPositions  # добавление пользовательских комплектующих
from calculators.calc_dispatcher.calculate_results import CalculateResults  # итоговый подсчет всех комплектующих
from calculators.calc_dispatcher.add_notes import AddNotes  # добавление пользовательских примечаний
from calculators.calc_dispatcher.render_console import RenderingConsole  # рендер расчёта (в текстовом виде)
from calculators.calc_dispatcher.rendering_html import RenderingHtml


class DispatcherCalcManager:
    def __init__(self, directory):
        self._directory = directory
        self._rules = rules  # в этой точке можно переопределить правила, не все
        self._price_update = BaseDispatcherUpdate(self._directory / "base")
        self._price_search = BaseDispatcherSearch(self._directory / "base")

    def update_price_ui(self):
        self._price_update.start()

    def update_price_console(self):
        """обновление прайс-листа"""
        print("=" * 50)
        print("~disp-update-price:Обновление прайс-листа диспетчерской мебели:")
        os.startfile(os.path.join(self._directory, "base", "price"))
        inp = input(
            "\t-Положите файл txt с прайсом в папку (в папке должен быть только 1 файл .txt)\n\t-Нажмите enter (или 0 если хотите отменить):>_")
        if inp == "0":
            print("отменено")
            return
        self._price_update.start()
        print("=" * 50)

    def calculate(self, tables: list, screens: list, montages: list, sockets: list, brackets: list,
                  table_name: str = None, user_postions: tuple = (), show_price=True, notes=None,
                  show_result_html=True, table_desk_price_map=(), side_wall_price=0,
                  ldsp_color=None, metal_color=None, ldsp_thikness=None, ldsp_price_area=None):
        """
        Менеджер расчета, объединяет все классы в кучу и производит последовательный расчёт. Все внешние приложения
        должны работать через него.
        :param notes: пользовательские примечания
        :param tables: цепочка модулей столов по длинам, пример [100,100,100]
        :param screens: цепочка экранов к столам (опционально), пример [45,0,45] # экран в центре отсутствует
        :param montages: цепочка шин монтажных к столам (опционально), пример [1,] # шина только к 1 столу
        :param sockets: [0,0] -> блоки розеток шт. , панели rj45 шт.
        :param brackets: кронштейны [0,0,0] # тип А - 1 низкая стойка 1 монитор, B - высокая стойка 2 монитора,
        C - высокая стойка 1 монитор.
        :param table_name: наименование изделия (необязательно)
        :param user_postions: пользовательские позиции добавляются в формате:
        :param show_price: показывать цены в прайсе? (иногда может требоваться выдать просто комплектацию без цен)
        :param show_result_html: выводить результат в виде html (для отладки можно и текст в консоли)
        user_postions=({"art": "001", "name": "пачка сосисок", "count": 1, "price": 0}
        :param table_desk_price_map: карта цен для столешниц (если задавать в ручную) [1000,1000]
        :param side_wall_price: переопределение стоимости боковин (можно задавать цены в ручную)
        :param ldsp_color: цвет ЛДСП # можно переопределять (стандартный арктика серый)
        :param metal_color: цвет металла # можно переопределять (стандартный RAL 7047)
        :param ldsp_thikness: толщина столешниц
        :return:
        """

        # print(tables)

        try:
            # I ВЫЧИСЛЕНИЯ:
            user_input = UserInput(
                tables=tables, screens=screens, montages=montages,
                sockets=sockets, brackets=brackets, rules=rules,
                table_name=table_name, ldsp_color=ldsp_color,
                ldsp_thikness=ldsp_thikness
            )  # проброс аргументов
            res = user_input.get_convert_parametrs()  # преобразование пользователских параметров
            # подключаемые классы модули (порядок вызвов важен), изменяют res наместе:
            GetBaseParametrs(
                moduls=res, base_search=self._price_search, rules=rules, metall_color=metal_color
            )  # получение позиций из БД
            # print(res)
            # input()
            rules['ldsp_price_area'] = ldsp_price_area if ldsp_price_area else rules['ldsp_price_area']
            LdspCalculate(
                moduls=res, rules=rules,
                table_desk_price_map=table_desk_price_map,
                side_wall_price=side_wall_price,
                ldsp_color=ldsp_color,
            )  # посчитать стоимость деталей из ЛДСП (боковины переезж в OPTIONS)
            ModulsCounter(moduls=res)  # убрать дублирующиеся модули поставив их количество
            AddUserPositions(moduls=res, user_positions=user_postions)  # добав пользовательских позиций (если есть)
            CalculateResults(moduls=res)  # подсчёт общей суммы модулей, а также цен групповых модулей
            AddNotes(moduls=res, notes=notes)  # добавление пользовательских примечаний

            # II РЕНДЕРИНГ РЕЗУЛЬТАТА:
            if show_result_html:
                text = RenderingHtml(moduls=res, rules=rules, show_price=show_price, directory=self._directory)
            else:
                text = RenderingConsole(res, rules, show_price=show_price)

            text.show_result()

        except Exception as err:
            raise Exception(f"Ошибка: {err}")


if __name__ == '__main__':
    disp_manager = DispatcherCalcManager(directory=os.path.join(os.getcwd()))
    # disp_manager.update_price_console()
    disp_manager.calculate(
        tables=[160, 90, 80],
        screens=[85, 85, 85],
        montages=[1, 1, 1],
        sockets=[2, 1],
        brackets=[0, 5, 0],
        show_price=True,
        metal_color="RAL 7047",
        # table_desk_price_map=[0, 0, 0, 0, 0],  # проброс цен столешниц в ручную (если потребуется)
        # ldsp_color="Бежевый песок",
        # side_wall_price=123,  # проброс цены боковин в ручную (если потребуется)
        # table_name="Стол угловой",
        notes=[
            'Максимальный вес монитора 8 кг.',
            'Внутренняя глубина технического отсека 350 мм.',
            'В модульных комплектующих детали указаны из расчета на 1 модуль',
            'Знак формата <span style="color:red">|==>x..</span> в заголовке модуля обозначает количество этих модулей.',
            'В модульных комплектующих (заголовок модуль) детали указаны из расчета на 1 модуль',
            'Знак формата ==><span style="color:red">x..</span>==> в отображении детали обозначает количество деталей.',
        ],
        show_result_html=False,
        # ниже опции, но их я реализую уже если время останется
        # user_postions=(
        #     {"art": "ФЛ-1201", "name": "Тумба выкатная, 42*55*60, Арктика серый.", "count": 4, "price": 16500},
        #     {"art": "ФЛ-1224", "name": "Стол приставной с тумбой двусторонней с ящиками 120х100х76, Арктика серый.",
        #      "count": 1, "price": 44000},
        # ),
        # user_postions=(
        #     {"art": "001", "name": "пачка сосисок", "count": 1, "price": 0},
        #     {"art": "002", "name": "маринованные огурчики", "count": 1000, "price": 0}
        # )
        # table_name="стол диспетчера угловой"
    )
