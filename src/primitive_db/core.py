from typing import List

from primitive_db.constants import VALID_TYPES
from primitive_db.utils import ensure_data_dir, load_metadata, save_metadata


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