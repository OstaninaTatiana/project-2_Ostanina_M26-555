import json
import os
from typing import Any, Dict, List

from primitive_db.constants import DATA_DIR, META_FILE


def ensure_data_dir() -> None:
    """Создает директорию для данных, если её нет."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_metadata() -> Dict[str, Any]:
    """Загружает метаданные из JSON-файла"""
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data: Dict[str, Any]) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_table_data(table_name: str) -> List[Dict[str, Any]]:
    """Загружает данные таблицы из JSON-файла"""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: List[Dict[str, Any]]) -> None:
    """Сохраняет данные таблицы в JSON-файл"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)