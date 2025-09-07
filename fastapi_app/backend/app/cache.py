import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
import hashlib
import os
from app.db import REDIS_URL

# Redis клиент
redis_client = None

async def get_redis():
    """Получает Redis клиент с lazy initialization"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=False)
    return redis_client

class CacheManager:
    """Менеджер кэширования с поддержкой различных типов данных"""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        try:
            redis_client = await get_redis()
            data = await redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Устанавливает значение в кэш"""
        try:
            redis_client = await get_redis()
            ttl = ttl or self.default_ttl
            serialized = pickle.dumps(value)
            return await redis_client.setex(key, ttl, serialized)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Удаляет значение из кэша"""
        try:
            redis_client = await get_redis()
            return bool(await redis_client.delete(key))
        except Exception:
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Удаляет все ключи по паттерну"""
        try:
            redis_client = await get_redis()
            keys = await redis_client.keys(pattern)
            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception:
            return 0
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерирует уникальный ключ кэша"""
        # Создаем хеш из аргументов
        key_parts = [prefix]
        
        # Добавляем позиционные аргументы
        for arg in args:
            key_parts.append(str(arg))
        
        # Добавляем именованные аргументы (сортированные для консистентности)
        for key in sorted(kwargs.keys()):
            key_parts.append(f"{key}:{kwargs[key]}")
        
        key_string = "|".join(key_parts)
        return f"hpi:{hashlib.md5(key_string.encode()).hexdigest()}"

# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()

def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """Декоратор для кэширования ответов API"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = cache_manager.generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Пытаемся получить из кэша
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Если нет в кэше, выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем результат в кэш
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """Декоратор для инвалидации кэша по паттерну"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Инвалидируем кэш
            await cache_manager.delete_pattern(pattern)
            
            return result
        return wrapper
    return decorator

# Специализированные функции кэширования для разных типов данных
async def cache_user_data(user_id: int, data: Any, ttl: int = 600):
    """Кэширует данные пользователя"""
    key = f"hpi:user:{user_id}:data"
    return await cache_manager.set(key, data, ttl)

async def get_cached_user_data(user_id: int) -> Optional[Any]:
    """Получает закэшированные данные пользователя"""
    key = f"hpi:user:{user_id}:data"
    return await cache_manager.get(key)

async def invalidate_user_cache(user_id: int):
    """Инвалидирует весь кэш пользователя"""
    pattern = f"hpi:user:{user_id}:*"
    return await cache_manager.delete_pattern(pattern)

async def cache_dashboard_data(user_id: int, date: str, data: Any, ttl: int = 300):
    """Кэширует данные дашборда"""
    key = f"hpi:dashboard:{user_id}:{date}"
    return await cache_manager.set(key, data, ttl)

async def get_cached_dashboard_data(user_id: int, date: str) -> Optional[Any]:
    """Получает закэшированные данные дашборда"""
    key = f"hpi:dashboard:{user_id}:{date}"
    return await cache_manager.get(key)

async def invalidate_dashboard_cache(user_id: int, date: str = None):
    """Инвалидирует кэш дашборда"""
    if date:
        key = f"hpi:dashboard:{user_id}:{date}"
        return await cache_manager.delete(key)
    else:
        pattern = f"hpi:dashboard:{user_id}:*"
        return await cache_manager.delete_pattern(pattern) 