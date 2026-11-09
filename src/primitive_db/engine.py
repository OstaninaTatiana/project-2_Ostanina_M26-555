import shlex

import prompt

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import parse_set, parse_values, parse_where


def print_help() -> None:
    """Выводит справочную информацию."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, ...) - "
          "создать запись"
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> - "
        "прочитать записи"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - "
        "удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
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

        try:
            _handle_command(command, args, user_input)
        except (KeyError, ValueError) as e:
            print(f"Ошибка: {e}")

        if command == "exit":
            break

def _handle_command(command: str, args: list, user_input: str) -> None:
    """Обрабатывает команду пользователя."""
    if command == "exit":
        print("Выход из программы.")
    elif command == "help":
        print_help()
    elif command == "list_tables":
        list_tables()
    elif command == "create_table":
        _handle_create_table(args)
    elif command == "drop_table":
        _handle_drop_table(args)
    elif command == "insert":
        _handle_insert(args, user_input)
    elif command == "select":
        _handle_select(args, user_input)
    elif command == "update":
        _handle_update(args, user_input)
    elif command == "delete":
        _handle_delete(args, user_input)
    elif command == "info":
        _handle_info(args)
    else:
        print(f"Функции '{command}' нет. Попробуйте снова.")


def _handle_create_table(args: list) -> None:
    """Обрабатывает команду create_table."""
    if len(args) < 3:
        raise ValueError(
            "Некорректное значение: недостаточно аргументов. "
            "Используйте: create_table <имя> <кол1:тип> ..."
        )
    create_table(args[1], args[2:])


def _handle_drop_table(args: list) -> None:
    """Обрабатывает команду drop_table."""
    if len(args) != 2:
        raise ValueError("Некорректное значение: используйте drop_table <имя_таблицы>")
    drop_table(args[1])


def _handle_insert(args: list, user_input: str) -> None:
    """Обрабатывает команду insert into <table> values (...)."""
    if len(args) < 5 or args[1].lower() != "into" or args[3].lower() != "values":
        raise ValueError(
            "Некорректный синтаксис. Используйте: "
            "insert into <таблица> values (<значения>)"
        )

    table_name = args[2]
    values_start = user_input.lower().find("values")
    if values_start == -1:
        raise ValueError("Не найдено ключевое слово 'values'")

    values_str = user_input[values_start + len("values"):].strip()
    values = parse_values(values_str)
    insert(table_name, values)


def _handle_select(args: list, user_input: str) -> None:
    """Обрабатывает команду select from <table> [where ...]."""
    if len(args) < 3 or args[1].lower() != "from":
        raise ValueError(
            "Некорректный синтаксис. Используйте: "
            "select from <таблица> [where <столбец> = <значение>]"
        )

    table_name = args[2]

    where_idx = _find_keyword(user_input, "where")
    if where_idx == -1:
        select(table_name)
    else:
        where_str = user_input[where_idx + len("where"):].strip()
        where_parts = shlex.split(where_str)
        where_clause = parse_where(where_parts)
        select(table_name, where_clause)


def _handle_update(args: list, user_input: str) -> None:
    """Обрабатывает команду update <table> set ... where ..."""
    if len(args) < 7:
        raise ValueError(
            "Некорректный синтаксис. Используйте: "
            "update <таблица> set <столбец> = <значение> where <столбец> = <значение>"
        )

    table_name = args[1]
    if args[2].lower() != "set":
        raise ValueError("Ожидалось ключевое слово 'set'")

    where_idx = _find_keyword(user_input, "where")
    if where_idx == -1:
        raise ValueError("Не найдено ключевое слово 'where'")

    set_str = user_input[
        user_input.lower().find("set") + len("set"):where_idx
    ].strip()
    where_str = user_input[where_idx + len("where"):].strip()

    set_clause = parse_set(shlex.split(set_str))
    where_clause = parse_where(shlex.split(where_str))
    update(table_name, set_clause, where_clause)


def _handle_delete(args: list, user_input: str) -> None:
    """Обрабатывает команду delete from <table> where ..."""
    if len(args) < 6 or args[1].lower() != "from":
        raise ValueError(
            "Некорректный синтаксис. Используйте: "
            "delete from <таблица> where <столбец> = <значение>"
        )

    table_name = args[2]
    where_idx = _find_keyword(user_input, "where")
    if where_idx == -1:
        raise ValueError("Не найдено ключевое слово 'where'")

    where_str = user_input[where_idx + len("where"):].strip()
    where_clause = parse_where(shlex.split(where_str))
    delete(table_name, where_clause)

def _handle_info(args: list) -> None:
    """Обрабатывает команду info <table>."""
    if len(args) != 2:
        raise ValueError("Некорректное значение: используйте info <имя_таблицы>")
    info(args[1])


def _find_keyword(text: str, keyword: str) -> int:
    """Ищет ключевое слово в строке, игнорируя регистр."""
    lower_text = text.lower()
    idx = lower_text.find(keyword)
    if idx == -1:
        return -1
    before_ok = idx == 0 or not lower_text[idx - 1].isalpha()
    after_ok = idx + len(keyword) >= len(lower_text) or not lower_text[
        idx + len(keyword)
    ].isalpha()
    return idx if before_ok and after_ok else -1
