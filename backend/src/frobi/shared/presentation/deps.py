"""Per-request infrastructure handles that module ``dependencies.py`` files build on."""

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from frobi.shared.domain import Clock


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    factory = cast(async_sessionmaker[AsyncSession], request.app.state.session_factory)
    async with factory() as session:
        yield session


def get_redis(request: Request) -> "Redis":
    return cast("Redis", request.app.state.redis)


def get_clock(request: Request) -> Clock:
    return cast(Clock, request.app.state.clock)
