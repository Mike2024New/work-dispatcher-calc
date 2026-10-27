import json
from pathlib import Path
from typing import Union, List


def read_json_file(file_path: Path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    return None


def rec_json_file(file_path: Path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as err:
        raise Exception(f"Ошибка при чтении json {err}")


def edit_json_value(file_path: Path, key_path: Union[str, List[str]], new_value) -> bool:
    """
    Редактирует значение в JSON-файле по ключу или по пути ключей.

    :param file_path: путь к JSON-файлу
    :param key_path: ключ или список ключей для вложенного доступа (например, ['user', 'name'])
    :param new_value: новое значение для установки
    :return: True, если успешно, False при ошибках
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Если key_path строка, приводим к списку для удобства
        if isinstance(key_path, str):
            key_path = [key_path]

        # Навигация по вложенным ключам
        d = data
        for key in key_path[:-1]:
            if key not in d or not isinstance(d[key], dict):
                print(f"Ключ '{key}' не найден или не является словарём.")
                return False
            d = d[key]

        # Изменяем значение по последнему ключу
        last_key = key_path[-1]
        if last_key not in d:
            print(f"Ключ '{last_key}' не найден.")
            return False

        d[last_key] = new_value

        # Сохраняем обратно в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True

    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return False


if __name__ == '__main__':
    pass
