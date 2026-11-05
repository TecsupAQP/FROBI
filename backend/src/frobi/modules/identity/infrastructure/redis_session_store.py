"""Sessions in Redis: ``session:{token} -> person_id`` with a 30-day TTL (PLAN_BACKEND §5)."""

import secrets
from collections.abc import Callable
from datetime import timedelta
from uuid import UUID

from redis.asyncio import Redis

SESSION_TTL = timedelta(days=30)


def _new_token() -> str:
    return secrets.token_urlsafe(32)


class RedisSessionStore:
    def __init__(
        self,
        redis: "Redis",
        ttl: timedelta = SESSION_TTL,
        token_factory: Callable[[], str] = _new_token,
    ) -> None:
        self._redis = redis
        self._ttl = ttl
        self._new_token = token_factory

    @staticmethod
    def _key(token: str) -> str:
        return f"session:{token}"

    async def create(self, person_id: UUID) -> str:
        token = self._new_token()
        await self._redis.set(self._key(token), str(person_id), ex=self._ttl)
        return token

    async def resolve(self, token: str) -> UUID | None:
        value = await self._redis.get(self._key(token))
        if not value:
            return None
        try:
            return UUID(str(value))
        except ValueError:
            return None

    async def revoke(self, token: str) -> None:
        await self._redis.delete(self._key(token))
