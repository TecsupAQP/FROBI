"""Wiring: builds tutoring's handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.tutoring.application import (
    GetAttemptHandler,
    OpenAttemptHandler,
    RequestStepHandler,
    SubmitOwnAnswerHandler,
)
from frobi.modules.tutoring.application.ports import HintGenerator
from frobi.modules.tutoring.infrastructure import (
    FallbackHintGenerator,
    LlmHintGenerator,
    ResilientHintGenerator,
    SqlAlchemyHelpAttemptRepository,
    TutoringContextReaderAdapter,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient, RedisRateLimiter
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_redis, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_hint_generator(
    redis: Annotated["Redis", Depends(get_redis)],
    llm: Annotated[LlmClient, Depends(get_llm)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HintGenerator:
    return ResilientHintGenerator(
        primary=LlmHintGenerator(llm),
        fallback=FallbackHintGenerator(),
        limiter=RedisRateLimiter(redis, settings.llm_requests_per_minute),
        timeout_seconds=settings.llm_timeout_seconds,
    )


def get_open_attempt(
    db: DbSession, clock: Annotated[Clock, Depends(get_clock)]
) -> OpenAttemptHandler:
    return OpenAttemptHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyHelpAttemptRepository(db),
        TutoringContextReaderAdapter(db),
        clock,
    )


def get_request_step(
    db: DbSession, hints: Annotated[HintGenerator, Depends(get_hint_generator)]
) -> RequestStepHandler:
    return RequestStepHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyHelpAttemptRepository(db),
        TutoringContextReaderAdapter(db),
        hints,
    )


def get_submit_own_answer(db: DbSession) -> SubmitOwnAnswerHandler:
    return SubmitOwnAnswerHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyHelpAttemptRepository(db),
        TutoringContextReaderAdapter(db),
    )


def get_get_attempt(db: DbSession) -> GetAttemptHandler:
    return GetAttemptHandler(SqlAlchemyHelpAttemptRepository(db))
