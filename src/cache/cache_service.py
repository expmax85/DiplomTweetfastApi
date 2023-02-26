import json

import aioredis

from src.config import settings

from .base_cache_service import AbstractCache


class RedisCache(AbstractCache):
    def __init__(self, redis_url: str) -> None:
        self.redis = aioredis.from_url(redis_url)

    async def set_cache(self, data: dict | list | None, key: str) -> None:
        if data:
            await self.redis.set(json.dumps(data), key)

    async def get_cache(self, key: str) -> list | dict | None:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def delete_cache(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_many(self, key_parent: str) -> None:
        async for key in self.redis.scan_iter(f"{key_parent}*"):
            await self.redis.delete(key)


def get_cache() -> RedisCache:
    return RedisCache(redis_url=settings.CACHE_URL)
