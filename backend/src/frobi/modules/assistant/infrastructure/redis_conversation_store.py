"""Conversations in Redis (``assistant:conversation:{person_id}``), shared by every API instance.

Kept for a week after the last answer; the person can also start a new one at any time.
"""

import json
from typing import TYPE_CHECKING
from uuid import UUID

from frobi.modules.assistant.domain import ChatLine, Conversation, Speaker

if TYPE_CHECKING:
    from redis.asyncio import Redis

TTL_SECONDS = 7 * 24 * 3600


def _key(person_id: UUID) -> str:
    return f"assistant:conversation:{person_id}"


class RedisConversationStore:
    def __init__(self, redis: "Redis") -> None:
        self._redis = redis

    async def load(self, person_id: UUID) -> Conversation:
        raw = await self._redis.get(_key(person_id))
        if raw is None:
            return Conversation()
        data = json.loads(raw)
        return Conversation(
            lines=tuple(ChatLine(Speaker(line["speaker"]), line["text"]) for line in data["lines"]),
            model_state=tuple(data["model_state"]),
        )

    async def save(self, person_id: UUID, conversation: Conversation) -> None:
        data = {
            "lines": [
                {"speaker": line.speaker.value, "text": line.text} for line in conversation.lines
            ],
            "model_state": list(conversation.model_state),
        }
        await self._redis.set(_key(person_id), json.dumps(data), ex=TTL_SECONDS)

    async def clear(self, person_id: UUID) -> None:
        await self._redis.delete(_key(person_id))
