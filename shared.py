import os
import shutil


# для БД
def custom_lower(string):
    return string.lower() if isinstance(string, str) else string


# для БД
def custom_upper(string):
    return string.upper() if isinstance(string, str) else string


def show_complect_in_consol(complect: dict) -> None:
    """
    # вывод комплекта в консоль
    :param complect: 1 комплект формата:
        {'art' : ... , 'name' : ... , details : [ { 'art' : ... , 'name' : ... , } ] }
    :return:
    """
    print('-' * 50)
    print(f"{complect['art']} | {complect['name']}:")
    for detail in complect['details']:
        print(f"    -{detail['art']}  {detail['name']} - {detail['count']} {detail['type']}")


def del_files_in_directory(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Не удалось удалить {}. причина: {}'.format(file_path, e))


def read_txt(path, split_row=False):
    with open(file=path, mode="r", encoding="utf-8") as txt:
        data = txt.read()
        if split_row:
            data = data.split("\n")
        return data
