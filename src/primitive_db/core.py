from typing import Any, Dict, List, Optional

from prettytable import PrettyTable

from primitive_db.constants import VALID_TYPES
from primitive_db.utils import (
    ensure_data_dir,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def create_table(table_name: str, columns: List[str]) -> None:
    """Создает новую таблицу с автоматическим добавлением ID:int"""
    metadata = load_metadata()

    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует.")

    final_columns = ["ID:int"]

    for col_def in columns:
        if ":" not in col_def:
            raise ValueError(
                f"Некорректное значение: {col_def}. Ожидался формат имя:тип"
            )

        name, col_type = col_def.split(":", 1)
        if col_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректный тип данных: {col_type}. Допустимы: {VALID_TYPES}"
            )

        final_columns.append(f"{name}:{col_type}")

    metadata[table_name] = {"columns": final_columns}
    save_metadata(metadata)
    ensure_data_dir()
    print(
        f"Таблица '{table_name}' успешно создана со столбцами: "
        f"{', '.join(final_columns)}"
    )


def drop_table(table_name: str) -> None:
    """Удаляет таблицу из метаданных"""
    metadata = load_metadata()

    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует")

    del metadata[table_name]
    save_metadata(metadata)
    print(f"Таблица '{table_name}' успешно удалена")


def list_tables() -> None:
    """Выводит список всех существующих таблиц"""
    metadata = load_metadata()
    if not metadata:
        print("Таблиц пока нет.")
        return

    print("Список таблиц:")
    for table in metadata.keys():
        print(f"- {table}")


def insert(table_name: str, values: List[Any]) -> None:
    """Добавляет новую запись в таблицу с автоматической генерацией ID."""
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    columns = metadata[table_name]["columns"]
    expected_count = len(columns) - 1

    if len(values) != expected_count:
        raise ValueError(
            f"Ожидалось {expected_count} значений (без ID), получено {len(values)}"
        )

    for i, value in enumerate(values):
        col_def = columns[i + 1]  # пропускаем ID
        col_name, col_type = col_def.split(":")
        if not _validate_type(value, col_type):
            raise ValueError(
                f"Некорректный тип для столбца '{col_name}': "
                f"ожидается {col_type}, получено {type(value).__name__}"
            )

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1

    new_row = {"ID": new_id}
    for i, value in enumerate(values):
        col_name = columns[i + 1].split(":")[0]
        new_row[col_name] = value

    data.append(new_row)
    save_table_data(table_name, data)
    print(f"Запись с ID={new_id} успешно добавлена в таблицу '{table_name}'.")


def select(table_name: str, where_clause: Optional[Dict[str, Any]] = None) -> None:
    """Выводит записи из таблицы, фильтруя по условию."""
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    data = load_table_data(table_name)
    columns = metadata[table_name]["columns"]

    if where_clause:
        filtered = []
        for row in data:
            match = True
            for col, val in where_clause.items():
                if col not in row or row[col] != val:
                    match = False
                    break
            if match:
                filtered.append(row)
        data = filtered

    table = PrettyTable()
    col_names = [c.split(":")[0] for c in columns]
    table.field_names = col_names

    for row in data:
        table.add_row([row.get(c, "") for c in col_names])

    print(table)


def update(
    table_name: str, set_clause: Dict[str, Any], where_clause: Dict[str, Any]
) -> None:
    """Обновляет записи в таблице по условию."""
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    data = load_table_data(table_name)
    updated_count = 0

    for row in data:
        match = all(row.get(k) == v for k, v in where_clause.items())
        if match:
            for col, val in set_clause.items():
                if col == "ID":
                    raise ValueError("Нельзя изменять столбец ID")
                row[col] = val
            updated_count += 1

    if updated_count == 0:
        print("Записей, удовлетворяющих условию, не найдено.")
        return

    save_table_data(table_name, data)
    print(f"В таблице '{table_name}' успешно обновлено записей: {updated_count}.")


def delete(table_name: str, where_clause: Dict[str, Any]) -> None:
    """Удаляет записи из таблицы по условию."""
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    data = load_table_data(table_name)
    initial_count = len(data)

    data = [
        row for row in data
        if not all(row.get(k) == v for k, v in where_clause.items())
    ]

    deleted_count = initial_count - len(data)
    if deleted_count == 0:
        print("Записей, удовлетворяющих условию, не найдено.")
        return

    save_table_data(table_name, data)
    print(f"Из таблицы '{table_name}' успешно удалено записей: {deleted_count}.")

def info(table_name: str) -> None:
    """Выводит информацию о структуре таблицы и количестве записей."""
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    columns = metadata[table_name]["columns"]
    data = load_table_data(table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(columns)}")
    print(f"Количество записей: {len(data)}")


def _validate_type(value: Any, expected_type: str) -> bool:
    """Проверяет, соответствует ли значение ожидаемому типу."""
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "str":
        return isinstance(value, str)
    if expected_type == "bool":
        return isinstance(value, bool)
    return False