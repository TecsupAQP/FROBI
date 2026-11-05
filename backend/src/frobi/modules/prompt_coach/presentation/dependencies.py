"""Wiring: builds prompt_coach's handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.prompt_coach.application import ComparePromptsHandler, EvaluatePromptHandler
from frobi.modules.prompt_coach.application.ports import PromptRunner, PromptScorer
from frobi.modules.prompt_coach.infrastructure import (
    LlmRunner,
    LlmScorer,
    MaterialLookupAdapter,
    ResilientRunner,
    ResilientScorer,
    RubricScorer,
    SimulatedRunner,
    SqlAlchemyEvaluationRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient, RedisRateLimiter
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_redis, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
RedisClient = Annotated["Redis", Depends(get_redis)]
Llm = Annotated[LlmClient, Depends(get_llm)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_scorer(redis: RedisClient, llm: Llm, settings: AppSettings) -> PromptScorer:
    return ResilientScorer(
        LlmScorer(llm),
        RubricScorer(),
        RedisRateLimiter(redis, settings.llm_requests_per_minute),
        settings.llm_timeout_seconds,
    )


def get_runner(redis: RedisClient, llm: Llm, settings: AppSettings) -> PromptRunner:
    return ResilientRunner(
        LlmRunner(llm),
        SimulatedRunner(),
        RedisRateLimiter(redis, settings.llm_requests_per_minute),
        settings.llm_timeout_seconds,
    )


def get_evaluate_prompt(
    db: DbSession,
    clock: Annotated[Clock, Depends(get_clock)],
    scorer: Annotated[PromptScorer, Depends(get_scorer)],
) -> EvaluatePromptHandler:
    return EvaluatePromptHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyEvaluationRepository(db),
        MaterialLookupAdapter(db),
        scorer,
        clock,
    )


def get_compare_prompts(
    db: DbSession, runner: Annotated[PromptRunner, Depends(get_runner)]
) -> ComparePromptsHandler:
    return ComparePromptsHandler(
        SqlAlchemyEvaluationRepository(db), MaterialLookupAdapter(db), runner
    )
