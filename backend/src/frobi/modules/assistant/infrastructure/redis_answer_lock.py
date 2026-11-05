"""``assistant:answering:{person_id}``: one answer at a time per person, on any instance.

The TTL frees the lock if an instance dies mid-answer.
"""

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from redis.asyncio import Redis

LOCK_SECONDS = 180


def _key(person_id: UUID) -> str:
    return f"assistant:answering:{person_id}"


class RedisAnswerLock:
    def __init__(self, redis: "Redis") -> None:
        self._redis = redis

    async def acquire(self, person_id: UUID) -> bool:
        return bool(await self._redis.set(_key(person_id), "1", nx=True, ex=LOCK_SECONDS))

    async def release(self, person_id: UUID) -> None:
        await self._redis.delete(_key(person_id))

    async def held(self, person_id: UUID) -> bool:
        return bool(await self._redis.exists(_key(person_id)))
