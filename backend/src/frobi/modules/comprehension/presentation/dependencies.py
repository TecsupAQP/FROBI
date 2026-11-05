"""Wiring: builds comprehension's handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.comprehension.application import AnswerQuestionHandler, GenerateQuestionsHandler
from frobi.modules.comprehension.application.ports import QuestionGenerator
from frobi.modules.comprehension.infrastructure import (
    FallbackQuestionGenerator,
    LlmQuestionGenerator,
    QuizContextReaderAdapter,
    ResilientQuestionGenerator,
    SqlAlchemyAnswerRepository,
    SqlAlchemyQuestionRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient, RedisRateLimiter
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_redis, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppClock = Annotated[Clock, Depends(get_clock)]


def get_question_generator(
    redis: Annotated["Redis", Depends(get_redis)],
    llm: Annotated[LlmClient, Depends(get_llm)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> QuestionGenerator:
    return ResilientQuestionGenerator(
        LlmQuestionGenerator(llm),
        FallbackQuestionGenerator(),
        RedisRateLimiter(redis, settings.llm_requests_per_minute),
        settings.llm_timeout_seconds,
    )


def get_generate_questions(
    db: DbSession,
    clock: AppClock,
    generator: Annotated[QuestionGenerator, Depends(get_question_generator)],
) -> GenerateQuestionsHandler:
    return GenerateQuestionsHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyQuestionRepository(db),
        QuizContextReaderAdapter(db),
        generator,
        clock,
    )


def get_answer_question(db: DbSession, clock: AppClock) -> AnswerQuestionHandler:
    return AnswerQuestionHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyQuestionRepository(db),
        SqlAlchemyAnswerRepository(db),
        clock,
    )
