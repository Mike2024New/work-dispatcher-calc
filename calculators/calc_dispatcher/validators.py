from calculators.calc_dispatcher.rules import rules


class Validators:
    """
    основные проверки калькулятора, начиная от входных парамтеров заканчивая размерами модулей и экранами
    """

    @staticmethod
    def validate_user_input_parametrs(tables, screens, montages, sockets, brackets) -> None:
        """
        Базовая проверка на корректность параметров введенных пользователем.
        :return: None (в случае найденной ошибки просто возбудить исключение)
        """
        # все параметры должны быть списками
        if not all(isinstance(inp, list) for inp in (tables, screens, montages, sockets, brackets)):
            raise ValueError("На вход принимаются только списки")

        # если не указан хотябы 1 стол
        if not tables:
            raise ValueError("Пустой список столов, должен быть указан хотябы 1 модуль")

        # все элементы списков должны быть целыми числами
        if not all(isinstance(inp, int) for inp in tables + screens + montages + sockets + brackets):
            raise ValueError("Указанные в списках параметры должны быть числами")

        # все элементы списков должны быть положительными
        if any(inp < 0 for inp in tables + screens + montages + sockets + brackets):
            raise ValueError("Указанные в списках параметры должны быть положительными числами")

        # правильность ввода размеров экранов
        if not all(inp in (rules["screens"]) for inp in screens):
            raise ValueError(f'Экраны могут быть указаны только в виде размеров: {rules["screens"]}')

        # правильность ввода параметров шин монтажных 0 шина есть, 1 шина отсутствует
        if not all(inp in (0, 1) for inp in montages):
            raise ValueError(f'Шины монтажные могут быть указаны в виде либо 0 (отсутствует), либо 1 (есть)')

        # проверка, что шины монтажные добавлены (если пользователь указал кронштейны для мониторов)
        if all(i == 0 for i in montages) and not all(i == 0 for i in brackets):
            raise ValueError("Указаны мониторы но нет шин монтажных, необходимо добавить хотябы 1 шину.")

    @staticmethod
    def validate_modul_table_length(check_key: str, modul_length: int) -> None:
        """
        проверка модулей столов который имеют разброс по длине (отдельностоящие,левые, правые, промежуточные)
        Не используется для угловых модулей, левых угловых, правых угловых.
        :param check_key: тип модуля из словаря проверок check_gabarits
        :param modul_length: длина модуля
        :return: None, в случае ошибки, возбуждает исключение
        """
        min_length = rules["tables"][check_key]["min"]
        max_length = rules["tables"][check_key]["max"]
        step_length = rules["tables"][check_key]["step"]
        name = rules["tables"][check_key]["name"]  # имя модуля для вывода в случае ошибки

        if modul_length not in range(min_length, max_length + step_length, step_length):
            raise ValueError(
                f"'{name}' 'L={modul_length}' должен быть размер от {min_length}  до {max_length}, с шагом {step_length}")

    @staticmethod
    def validate_user_positions(user_postions):
        """проверка введенных пользователем позиций в ручную (для add_user_positions)"""
        for pos in user_postions:
            err_msg = None

            if "art" not in pos:
                err_msg = "должен быть указан ключ артикула, данного ключа нет в словаре. а должен быть"
            if "name" not in pos:
                err_msg = "должно быть указано наименование позиции, данного ключа нет в словаре. а должен быть"
            if "price" not in pos:
                err_msg = "должно быть указана цена позиции, данного ключа нет в словаре. а должен быть"
            if "count" not in pos:
                err_msg = "должно быть указано количество позиций, данного ключа нет в словаре. а должен быть"

            if err_msg:
                raise Exception(f"Ошибка добавления пользовательской позиции {pos}\n {err_msg}\n"
                                f"Правильный формат добавляемых позиций art:...,name:..., price:..., count:... ")
