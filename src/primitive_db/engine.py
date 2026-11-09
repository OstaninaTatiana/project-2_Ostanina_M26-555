import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables


def print_help() -> None:
    """Выводит справочную информацию."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Основной цикл программы."""
    print("Первая попытка запустить проект!")
    print_help()

    while True:
        user_input = prompt.string(">>> Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга команды: {e}")
            continue

        command = args[0].lower()

        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            list_tables()
        elif command == "create_table":
            if len(args) < 3:
                print(
                    "Некорректное значение: недостаточно аргументов. "
                    "Используйте: create_table <имя> <кол1:тип> ..."
                )
                continue
            table_name = args[1]
            columns = args[2:]
            try:
                create_table(table_name, columns)
            except ValueError as e:
                print(f"Ошибка: {e}")
        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение: используйте drop_table <имя_таблицы>")
                continue
            table_name = args[1]
            try:
                drop_table(table_name)
            except KeyError as e:
                print(f"Ошибка: {e}")
        else:
            print(f"Функции '{command}' нет. Попробуйте снова.")