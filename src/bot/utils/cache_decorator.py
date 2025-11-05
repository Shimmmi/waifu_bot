"""
Cache decorator for API endpoints
"""
from functools import wraps
from typing import Callable, Any
from bot.services.cache_service import cache_service


def cached(ttl_seconds: int = 30, key_prefix: str = ""):
    """Декоратор для кэширования результатов функции"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаём ключ кэша
            cache_key = f"{key_prefix}:{cache_service.make_key(*args, **kwargs)}"
            
            # Проверяем кэш
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_service.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator
