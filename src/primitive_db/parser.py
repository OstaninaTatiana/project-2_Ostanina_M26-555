from typing import Any, Dict, List


def parse_values(values_str: str) -> List[str]:
    """Разбирает строку вида '(\"Sergei\", 28, true)' в список значений."""
    # Убираем скобки по краям
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

    values = []
    current = ""
    in_quotes = False
    quote_char = None

    for char in values_str:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == "," and not in_quotes:
            values.append(current.strip())
            current = ""
        else:
            current += char

    if current.strip():
        values.append(current.strip())

    return values


def parse_where(where_parts: List[str]) -> Dict[str, Any]:
    """Разбирает where-условие вида ['age', '=', '28'] в словарь {'age': 28}."""
    if len(where_parts) != 3:
        raise ValueError("Некорректное условие WHERE. Формат: <столбец> = <значение>")

    column, operator, value = where_parts
    if operator != "=":
        raise ValueError(f"Неподдерживаемый оператор: {operator}. Используйте '='")

    return {column: _convert_value(value)}


def parse_set(set_parts: List[str]) -> Dict[str, Any]:
    """Разбирает set-условие вида ['age', '=', '29'] в словарь {'age': 29}."""
    if len(set_parts) != 3:
        raise ValueError("Некорректное условие SET. Формат: <столбец> = <значение>")

    column, operator, value = set_parts
    if operator != "=":
        raise ValueError(f"Неподдерживаемый оператор: {operator}. Используйте '='")

    return {column: _convert_value(value)}


def _convert_value(value: str) -> Any:
    """Преобразует строковое значение в нужный тип Python."""
    value = value.strip()

    # Строка в кавычках
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    # Булево
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Целое число
    try:
        return int(value)
    except ValueError:
        pass

    raise ValueError(f"Некорректное значение: {value}")