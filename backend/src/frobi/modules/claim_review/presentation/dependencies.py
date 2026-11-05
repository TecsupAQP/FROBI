"""Wiring: builds claim_review's handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.claim_review.application import GetReviewHandler, ReviewClaimsHandler
from frobi.modules.claim_review.application.ports import ClaimReviewer
from frobi.modules.claim_review.infrastructure import (
    GuideReaderAdapter,
    LlmReviewer,
    ResilientReviewer,
    RuleBasedReviewer,
    SqlAlchemyClaimRepository,
    WorkReaderAdapter,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient, RedisRateLimiter
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_redis, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_reviewer(
    redis: Annotated["Redis", Depends(get_redis)],
    llm: Annotated[LlmClient, Depends(get_llm)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ClaimReviewer:
    return ResilientReviewer(
        LlmReviewer(llm),
        RuleBasedReviewer(),
        RedisRateLimiter(redis, settings.llm_requests_per_minute),
        settings.llm_timeout_seconds,
    )


def get_review_claims(
    db: DbSession,
    clock: Annotated[Clock, Depends(get_clock)],
    reviewer: Annotated[ClaimReviewer, Depends(get_reviewer)],
) -> ReviewClaimsHandler:
    return ReviewClaimsHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyClaimRepository(db),
        WorkReaderAdapter(db),
        GuideReaderAdapter(db),
        reviewer,
        clock,
    )


def get_get_review(db: DbSession) -> GetReviewHandler:
    return GetReviewHandler(SqlAlchemyClaimRepository(db), WorkReaderAdapter(db))
