"""Per-person AI call budget: ``ratelimit:ai:{person_id}`` counts calls in a 60 s window."""

from typing import Protocol
from uuid import UUID

from redis.asyncio import Redis

WINDOW_SECONDS = 60


class RateLimiter(Protocol):
    async def allow(self, person_id: UUID) -> bool: ...


class AllowAll:
    async def allow(self, person_id: UUID) -> bool:
        return True


class RedisRateLimiter:
    def __init__(self, redis: "Redis", per_minute: int) -> None:
        self._redis = redis
        self._per_minute = per_minute

    async def allow(self, person_id: UUID) -> bool:
        key = f"ratelimit:ai:{person_id}"
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, WINDOW_SECONDS)
        return int(count) <= self._per_minute
