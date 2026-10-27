class ModulsCounter:
    """удаление дубликатов модулей, подсчёт модулей"""

    def __init__(self, moduls):
        self._moduls = moduls
        self._moduls_count()

    def _moduls_count(self):
        """
        бывает что центаральные модули повторяются, имеют одинаковую длину, шину монтажну и экран
        в этой точке происходит их объединение а у модульной коллекции появляются два новый ключ
        count который показывает их количество
        """
        moduls_list = self._moduls["moduls"]

        count_elements = {}  # подсчет элементов
        viewed_element = []  # просмотренные элементы

        for i in range(len(moduls_list)):
            if moduls_list[i] not in viewed_element:
                count = moduls_list.count(moduls_list[i])
                count_elements[i] = {"index": i, "count": count}
                viewed_element.append(moduls_list[i])

        del viewed_element
        keys = sorted([key for key in count_elements])  # порядок очень важен! в старых python словари не упорядочены
        out_array = []  # выходная коллекция

        for key in keys:
            moduls_list[key]["count"] = count_elements[key]["count"]
            out_array.append(moduls_list[key])

        self._moduls["moduls"] = out_array

    def get_convert_parametrs(self):
        return self._moduls
