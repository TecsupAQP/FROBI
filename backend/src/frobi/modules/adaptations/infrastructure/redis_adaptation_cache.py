"""``adapt:{hash}`` (24 h) and ``lock:adapt:{hash}`` (20 s) in Redis (PLAN_BACKEND §5)."""

import json
import logging
from datetime import timedelta

from pydantic import ValidationError
from redis.asyncio import Redis

from frobi.modules.adaptations.domain import AdaptedContent

from .content_codec import content_from_json, content_to_json

logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(hours=24)
LOCK_TTL = timedelta(seconds=20)


class RedisAdaptationCache:
    def __init__(self, redis: "Redis") -> None:
        self._redis = redis

    async def get(self, key: str) -> AdaptedContent | None:
        raw = await self._redis.get(f"adapt:{key}")
        if not raw:
            return None
        try:
            return content_from_json(json.loads(raw))
        except (ValueError, ValidationError):
            logger.warning("Discarding a corrupt cached adaptation")
            return None

    async def put(self, key: str, content: AdaptedContent) -> None:
        payload = json.dumps(content_to_json(content), ensure_ascii=False)
        await self._redis.set(f"adapt:{key}", payload, ex=CACHE_TTL)

    async def try_lock(self, key: str) -> bool:
        return bool(await self._redis.set(f"lock:adapt:{key}", "1", nx=True, ex=LOCK_TTL))

    async def unlock(self, key: str) -> None:
        await self._redis.delete(f"lock:adapt:{key}")
