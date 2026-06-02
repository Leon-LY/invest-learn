"""Redis cache helper."""
import json
from typing import Optional, Any
from redis.asyncio import Redis
from .config import settings

_redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Returns a shared Redis connection."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value by key, deserializing from JSON."""
    r = await get_redis()
    val = await r.get(key)
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, TypeError):
        return val


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    """Set a cache value with TTL in seconds, serializing to JSON."""
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=float))


async def cache_delete(key: str) -> None:
    """Delete a cache key."""
    r = await get_redis()
    await r.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern."""
    r = await get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)
