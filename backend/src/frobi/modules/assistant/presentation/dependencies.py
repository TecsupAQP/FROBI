"""Wiring: builds the assistant's handlers with their adapters."""

from typing import TYPE_CHECKING, Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.assistant.application import AskAssistantHandler, ConversationHandler
from frobi.modules.assistant.application.ports import AssistantModel
from frobi.modules.assistant.infrastructure import (
    RedisAnswerLock,
    RedisConversationStore,
    RedisHub,
    StudyDataAdapter,
)
from frobi.shared.infrastructure import Settings
from frobi.shared.infrastructure.llm import RedisRateLimiter
from frobi.shared.presentation import get_redis

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from starlette.datastructures import State


def get_hub(request: Request) -> RedisHub:
    return cast(RedisHub, request.app.state.assistant_hub)


def get_conversation_handler(
    redis: Annotated["Redis", Depends(get_redis)],
) -> ConversationHandler:
    return ConversationHandler(RedisConversationStore(redis), RedisAnswerLock(redis))


def ask_handler(state: "State", session: AsyncSession) -> AskAssistantHandler:
    """Built per question (the WebSocket has no per-request dependencies)."""
    redis = cast("Redis", state.redis)
    settings = cast(Settings, state.settings)
    return AskAssistantHandler(
        cast(AssistantModel, state.assistant),
        RedisConversationStore(redis),
        StudyDataAdapter(session),
        RedisRateLimiter(redis, settings.llm_requests_per_minute),
        RedisAnswerLock(redis),
    )
