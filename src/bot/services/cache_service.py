"""
Cache service with TTL support for optimizing frequent database queries
"""
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Запись кэша с TTL"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class CacheService:
    """Сервис кэширования с TTL"""
    
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = 1000  # Максимальное количество записей
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        entry = self._cache.get(key)
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 30) -> None:
        """Сохранить значение в кэш"""
        # Очистка устаревших записей при достижении лимита
        if len(self._cache) >= self._max_size:
            self._cleanup_expired()
            # Если всё ещё переполнен, удаляем самые старые
            if len(self._cache) >= self._max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].expires_at)
                del self._cache[oldest_key]
        
        self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str) -> None:
        """Удалить значение из кэша"""
        self._cache.pop(key, None)
    
    def delete_pattern(self, pattern: str) -> None:
        """Удалить все ключи, начинающиеся с pattern"""
        keys_to_delete = [key for key in self._cache.keys() if key.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]
        if keys_to_delete:
            logger.debug(f"🗑️ Deleted {len(keys_to_delete)} cache entries matching pattern: {pattern}")
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        self._cache.clear()
        logger.debug("🗑️ Cache cleared")
    
    def _cleanup_expired(self) -> None:
        """Удалить все устаревшие записи"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"🗑️ Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_or_set(self, key: str, factory: Callable[[], Any], ttl_seconds: int = 30) -> Any:
        """Получить из кэша или вычислить и сохранить"""
        value = self.get(key)
        if value is not None:
            return value
        
        value = factory()
        self.set(key, value, ttl_seconds)
        return value
    
    def make_key(self, *args, **kwargs) -> str:
        """Создать ключ кэша из аргументов"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def stats(self) -> dict:
        """Получить статистику кэша"""
        expired_count = sum(1 for entry in self._cache.values() if entry.is_expired())
        return {
            'total_entries': len(self._cache),
            'expired_entries': expired_count,
            'active_entries': len(self._cache) - expired_count,
            'max_size': self._max_size
        }


# Глобальный экземпляр
cache_service = CacheService()
