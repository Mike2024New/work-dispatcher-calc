import os
import re
import sqlite3
from pathlib import Path

from shared import read_txt


class _BaseDispatcher:
    def __init__(self, directory):
        self.directory = directory
        self.base_path = directory / "dispatcher_price.db" #
        # self.base_path = os.path.join(directory, "dispatcher_price.db")
        self._con = sqlite3.connect(self.base_path)
        self._cursor = self._con.cursor()
        self._create_table()

    def _create_table(self):
        try:
            self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS price (
                art TEXT PRIMARY KEY NOT NULL,
                name TEXT,
                len INTEGER,
                type TEXT,
                price INTEGER
                )
            """)
            self._con.commit()
        except Exception as err:
            self._con.rollback()  # откатить изменения
            self._close()  # закрыть соединение с БД
            raise Exception(f'Ошибка при создании таблиц: {err}')

    def _close(self):
        if self._con:
            self._con.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()


class BaseDispatcherUpdate(_BaseDispatcher):
    """
    обновление прайс листа
    Для использования:
    1. Создать экземпляр класса, указав путь к директории этого проекта (где лежит этот модуль base_manager.py)
    2. Запустить обновление вызвав метод start (важно в папке должен быть 1 файл txt с прайс листом).

    bsd = BaseDispatcherUpdate(directory=os.getcwd())
    bsd.start()
    """

    def __init__(self, directory):
        super().__init__(directory)

    def start(self):
        """загрузка прайс-листа"""
        files = [file for file in os.listdir(os.path.join(self.directory, "price")) if file.endswith(".txt")]
        price = read_txt(path=os.path.join(self.directory, "price", files[0]), split_row=True)
        print(f"загрузка деталей в прайс-лист из файла '{files[0]}'...")
        self.sort_details_and_add_in_price(price)  # сортировка деталей по категориям и добавление их в прайс лист
        print(f"...прайс-лист обновлен")

    def sort_details_and_add_in_price(self, price):
        """
        Распределение изделий по категориям
        :param price:
        :return:
        """
        for detail in price:
            position = None
            if re.search(r"ФЛ-100[1-8]", detail):  # прямые модули столов
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Стол для диспетчера",
                    detail_type="table"
                )
            elif re.search(r"ФЛ-11[0-3][13579]", detail):  # левые модули столов
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Модуль стола левый",
                    detail_type="table_left"
                )
            elif re.search(r"ФЛ-11[0-3][02468]", detail):  # правые модули столов
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Модуль стола правый",
                    detail_type="table_right"
                )
            elif re.search(r"ФЛ-11[56][0-9]", detail):  # промежуточные модули столов
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Модуль стола промежуточный",
                    detail_type="table_mid"
                )
            elif re.search(r"ФЛ-1170", detail):  # стол угловой 90
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="модуль стола угловой 90º",
                    detail_type="table_angle_90"
                )

            elif re.search(r"ФЛ-1171", detail):  # стол угловой 22.5
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="модуль стола угловой 22.5º промежуточный",
                    detail_type="table_angle_22"
                )

            elif re.search(r"ФЛ-1141", detail):  # стол угловой левый 22.5
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="модуль стола угловой 22.5º левый",
                    detail_type="table_angle_22_l"
                )

            elif re.search(r"ФЛ-1142", detail):  # стол угловой правый 22.5
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="модуль стола угловой 22.5º правый",
                    detail_type="table_angle_22_r"
                )

            elif re.search(r"ФЛ-150[0-8]\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный стола",
                    detail_type="screen"
                )

            elif re.search(r"ФЛ-150[0-8]\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный стола",
                    detail_type="screen"
                )

            elif re.search(r"ФЛ-16[0-3][13579]\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный модуля левый",
                    detail_type="screen_left"
                )

            elif re.search(r"ФЛ-16[0-3][13579]\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный модуля левый",
                    detail_type="screen_left"
                )

            elif re.search(r"ФЛ-16[0-3][02468]\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный модуля правый",
                    detail_type="screen_right"
                )

            elif re.search(r"ФЛ-16[0-3][02468]\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный модуля правый",
                    detail_type="screen_right"
                )

            elif re.search(r"ФЛ-16[56][0-9]\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный модуля промежуточный",
                    detail_type="screen_mid"
                )

            elif re.search(r"ФЛ-16[56][0-9]\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный модуля промежуточный",
                    detail_type="screen_mid"
                )

            elif re.search(r"ФЛ-1670\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 90º",
                    detail_type="screen_angle_90",
                    length=100  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1670\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 90º",
                    detail_type="screen_angle_90",
                    length=100  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1671\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 22º",
                    detail_type="screen_angle_22",
                    length=100  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1671\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 22º",
                    detail_type="screen_angle_22",
                    length=100  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1641\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 22º левый",
                    detail_type="screen_angle_22_l",
                    length=120  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1641\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 22º левый",
                    detail_type="screen_angle_22_l",
                    length=120  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1642\.45", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 22º правый",
                    detail_type="screen_angle_22_r",
                    length=120  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-1642\.85", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Экран настольный угловой 22º правый",
                    detail_type="screen_angle_22_r",
                    length=120  # для этого модуля габарит прописывается отсюда напрямую, так как в прайсе его не указ
                )

            elif re.search(r"ФЛ-19[0-1][0-9]", detail):
                position = self.detail_extract_properties_schine(
                    detail_row=detail,
                    detail_name="Шина монтажная",
                    detail_type="montage"
                )

            elif re.search(r"ФЛ-1701", detail):
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Опора модуля промежуточная",
                    detail_type="support_table_modul",
                    length=0
                )

            elif re.search(r"ФЛ-1711", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Стойка экрана промежуточная",
                    detail_type="support_screen",
                    length=0
                )

            elif re.search(r"ФЛ-1715", detail):
                position = self.detail_extract_properties_screen(
                    detail_row=detail,
                    detail_name="Стойка кронштейна под монитор",
                    detail_type="support_bracket_monitor",
                    length=0
                )

            elif re.search(r"ФЛ-1721", detail):
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Кронштейн под монитор",
                    detail_type="bracket_monitor",
                    length=0
                )

            elif re.search(r"ФЛ-17[23][1-3]", detail):
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name=re.search(r"ФЛ-\d{4}\s(.+?)\s\d{1,3}\s\d{1,3}\s[₽Рр]", detail)[1],
                    detail_type="power_connector",
                    length=0
                )

            elif re.search(r"ФЛ-1740", detail):
                position = self.detail_extract_properties_modul(
                    detail_row=detail,
                    detail_name="Стеллаж внутренний",
                    detail_type="options",
                    length=0
                )

            if position:
                self.detail_add(detail=position)

    @staticmethod
    def detail_extract_properties_modul(detail_row, detail_name, detail_type, length=None):
        """извлечение параметров для столов и модулей"""
        try:
            detail = {
                "art": re.search(r"ФЛ-\d{4}", detail_row)[0],
                "name": detail_name,
                "len": length if length is not None else int(
                    re.search(r"(\d{2,3})[xх*]\d{2,3}[xх*]\d{2,3}", detail_row)[1]),
                "type": detail_type,
                "price": int(re.search(r"\s(\d{1,3}\s\d{1,3})\s[₽Рр]", detail_row)[1].replace(" ", "")),
            }
            return detail
        except Exception as err:
            print(f"Возникла ошибка при обработке [{detail_row}] -> {err}")
            return None

    @staticmethod
    def detail_extract_properties_screen(detail_row, detail_name, detail_type, length=None):
        """извлечение параметров для столов и модулей"""
        try:
            detail = {
                "art": re.search(r"ФЛ-\d{4}\.\d{2}", detail_row)[0],
                "name": detail_name,
                "len": length if length is not None else int(re.search(r"\s(\d{2,3})\sh=", detail_row)[1]),
                "type": detail_type,
                "price": int(re.search(r"\s(\d{1,3}\s\d{1,3})\s[₽Рр]", detail_row)[1].replace(" ", "")),
            }
            return detail
        except Exception as err:
            print(f"Возникла ошибка при обработке [{detail_row}] -> {err}")
            return None

    @staticmethod
    def detail_extract_properties_schine(detail_row, detail_name, detail_type):
        """извлечение параметров для столов и модулей"""
        try:
            detail = {
                "art": re.search(r"ФЛ-\d{4}", detail_row)[0],
                "name": detail_name,
                "len": int(re.search(r"L=(\d{2,3})", detail_row)[1]),
                "type": detail_type,
                "price": int(re.search(r"\s(\d{1,3}\s\d{1,3})\s[₽Рр]", detail_row)[1].replace(" ", "")),  # noqa
            }
            return detail
        except Exception as err:
            print(f"Возникла ошибка при обработке [{detail_row}] -> {err}")
            return None

    def detail_add(self, detail: dict) -> None:
        """CRUD - добавление/обновление детали в БД"""
        try:
            self.detail_delete(art=detail["art"])  # сперва удалять старую деталь если она уже существует
            self._cursor.execute(
                """INSERT INTO price(art,name,len,type,price) VALUES(?,?,?,?,?)""",
                (detail["art"], detail["name"], detail["len"], detail["type"], detail["price"])
            )
            self._con.commit()
        except Exception as err:
            print(f"Ошибка при добавлении детали {detail['art']} -> {err}")

    def detail_delete(self, art: str) -> None:
        """CRUD - удаление детали из БД по артикулу"""
        try:
            self._cursor.execute("""DELETE FROM price WHERE art = ?;""", (art,))
            self._con.commit()
        except Exception as err:
            print(f"Ошибка при удалении детали {art} -> {err}")


class BaseDispatcherSearch(_BaseDispatcher):
    def __init__(self, directory):
        super().__init__(directory)

    # получение детали по артикулу
    def get_detail_by_art(self, art):
        self._cursor.execute("""SELECT * FROM price WHERE art = ?""", (art,))
        res = self._cursor.fetchall()
        if res:
            return res
        return None

    # подходит для столов типа ФЛ-1001, шин монтажных
    def get_detail_by_len_type(self, length=80, detail_type="table"):
        """
        Пример вызова:
            get_detail_by_len_type(length=80, detail_type="table")
        """
        self._cursor.execute(
            """SELECT * FROM price WHERE len=? AND type=? LIMIT 1""",
            (length, detail_type)
        )
        res = self._cursor.fetchall()
        if res:
            return res
        return None

    # поиск подходит для экранов так как их высоты прописаны в артикулах
    def get_detail_by_height_len_type(self, height=45, length=80, detail_type="screen"):
        """
        Пример вызова:
            get_detail_by_height_len_type(height=45, length=80, detail_type="screen")
        """
        self._cursor.execute(
            """SELECT * FROM price WHERE art LIKE ? AND len=? AND type=? LIMIT 1""",
            (f"%.{height}", length, detail_type)
        )
        res = self._cursor.fetchall()
        if res:
            return res
        return None

    def get_list_details_by_type(self, type_detail, like=True):
        """
        Поиск деталей по типам, например для ui
        :param type_detail: тип искомой детали
        :param like: искать по части типа модуля, то есть like запрос % %, или без % (что по сути обознач строгое равенство)
        :return:
        """
        parametr = (f"%{type_detail}%",) if like else (f"{type_detail}",)
        self._cursor.execute(
            """SELECT * FROM price WHERE type LIKE ?""",
            parametr
        )
        res = self._cursor.fetchall()
        if res:
            return res
        return None


if __name__ == '__main__':
    bds = BaseDispatcherSearch(directory=os.getcwd())
    print(bds.get_detail_by_len_type(length=80, detail_type="table"))
    print(bds.get_detail_by_height_len_type(height=45, length=80, detail_type="screen"))
    print(bds.get_detail_by_len_type(length=60, detail_type="schine"))
