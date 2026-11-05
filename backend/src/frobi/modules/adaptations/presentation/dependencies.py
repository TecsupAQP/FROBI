"""Wiring: builds adaptations' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.adaptations.application import (
    CreateAdaptationHandler,
    GetAdaptationHandler,
    ListFormatsHandler,
)
from frobi.modules.adaptations.application.ports import TextGenerator
from frobi.modules.adaptations.infrastructure import (
    FallbackTextGenerator,
    LlmTextGenerator,
    MaterialReaderAdapter,
    ProfileReaderAdapter,
    RedisAdaptationCache,
    ResilientTextGenerator,
    SqlAlchemyAdaptationRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient, RedisRateLimiter
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_redis, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
RedisClient = Annotated["Redis", Depends(get_redis)]


def get_text_generator(
    redis: RedisClient,
    llm: Annotated[LlmClient, Depends(get_llm)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TextGenerator:
    return ResilientTextGenerator(
        primary=LlmTextGenerator(llm),
        fallback=FallbackTextGenerator(),
        limiter=RedisRateLimiter(redis, settings.llm_requests_per_minute),
        timeout_seconds=settings.llm_timeout_seconds,
    )


def get_list_formats(db: DbSession) -> ListFormatsHandler:
    return ListFormatsHandler(ProfileReaderAdapter(db))


def get_create_adaptation(
    db: DbSession,
    redis: RedisClient,
    clock: Annotated[Clock, Depends(get_clock)],
    generator: Annotated[TextGenerator, Depends(get_text_generator)],
) -> CreateAdaptationHandler:
    return CreateAdaptationHandler(
        uow=SqlAlchemyUnitOfWork(db),
        adaptations=SqlAlchemyAdaptationRepository(db),
        materials=MaterialReaderAdapter(db),
        profiles=ProfileReaderAdapter(db),
        generator=generator,
        cache=RedisAdaptationCache(redis),
        clock=clock,
    )


def get_get_adaptation(db: DbSession) -> GetAdaptationHandler:
    return GetAdaptationHandler(SqlAlchemyAdaptationRepository(db))
