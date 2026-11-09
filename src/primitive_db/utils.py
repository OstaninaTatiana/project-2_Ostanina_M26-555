import json
import os
from typing import Any, Dict

from primitive_db.constants import DATA_DIR, META_FILE


def ensure_data_dir() -> None:
    """Создает директорию для данных, если её нет."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_metadata() -> Dict[str, Any]:
    """Загружает метаданные из JSON-файла. Возвращает пустой dict, если файла нет."""
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data: Dict[str, Any]) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)