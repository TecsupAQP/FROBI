"""Wiring: builds identity's handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.identity.application import (
    DemoSessionHandler,
    EndSessionHandler,
    GetMeHandler,
    StartSessionHandler,
)
from frobi.modules.identity.infrastructure import (
    ClassroomsDemoDirectory,
    ClassroomsMembershipAdapter,
    RedisSessionStore,
    SettingsOnboardingStatus,
    SqlAlchemyPersonRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.presentation import get_clock, get_db_session, get_redis, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
RedisClient = Annotated["Redis", Depends(get_redis)]


def get_start_session(
    db: DbSession, redis: RedisClient, clock: Annotated[Clock, Depends(get_clock)]
) -> StartSessionHandler:
    return StartSessionHandler(
        uow=SqlAlchemyUnitOfWork(db),
        persons=SqlAlchemyPersonRepository(db),
        sessions=RedisSessionStore(redis),
        memberships=ClassroomsMembershipAdapter(db),
        clock=clock,
    )


def get_end_session(redis: RedisClient) -> EndSessionHandler:
    return EndSessionHandler(RedisSessionStore(redis))


def get_get_me(db: DbSession) -> GetMeHandler:
    return GetMeHandler(
        persons=SqlAlchemyPersonRepository(db),
        memberships=ClassroomsMembershipAdapter(db),
        onboarding=SettingsOnboardingStatus(db),
    )


DEMO_ENVIRONMENTS = frozenset({"local", "demo"})


def get_demo_session(
    db: DbSession, redis: RedisClient, settings: Annotated[Settings, Depends(get_settings)]
) -> DemoSessionHandler:
    return DemoSessionHandler(
        persons=SqlAlchemyPersonRepository(db),
        sessions=RedisSessionStore(redis),
        memberships=ClassroomsMembershipAdapter(db),
        demo=ClassroomsDemoDirectory(db),
        enabled=settings.environment in DEMO_ENVIRONMENTS,
    )
