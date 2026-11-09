import time
from functools import wraps
from typing import Any, Callable, Dict

import prompt


def handle_db_errors(func: Callable) -> Callable:
    """Декоратор для централизованной обработки ошибок БД."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
        return None
    return wrapper


def confirm_action(action_name: str) -> Callable:
    """Декоратор для запроса подтверждения опасных действий."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            answer = prompt.string(
                f"Вы уверены, что хотите выполнить \"{action_name}\"? [y/n]: "
            ).strip().lower()
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func: Callable) -> Callable:
    """Декоратор для замера времени выполнения функции."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result
    return wrapper


_cache: Dict[str, Any] = {}


def create_cacher() -> Callable:
    """Фабрика замыкания для кэширования результатов."""
    def cache_result(key: str, value_func: Callable) -> Any:
        if key in _cache:
            return _cache[key]
        result = value_func()
        _cache[key] = result
        return result

    return cache_result


def clear_cache() -> None:
    """Очищает кэш после операций, изменяющих данные."""
    _cache.clear()