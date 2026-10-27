"""вспомогательный скрипт, чтобы не копировать конспекты из отдельных файлов"""
import os


def read_file(path):
    with open(file=path, mode="r", encoding="utf-8") as f:
        try:
            return f.read()
        except Exception as err:
            print(f"Ошибка чтения файла {path} \n {err}")


def show_code_from_files(directory):
    for file in os.listdir(directory):
        full_path = os.path.join(os.getcwd(), file)
        if os.path.isfile(full_path) and file.endswith(".py"):
            print("=" * 50)
            print(f"Файл {file}:\n")
            print(read_file(path=full_path))


if __name__ == '__main__':
    show_code_from_files(directory=os.getcwd())
