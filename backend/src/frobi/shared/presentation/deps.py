"""Per-request infrastructure handles that module ``dependencies.py`` files build on."""

from collections.abc import AsyncIterator
from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from frobi.shared.application import ClassContext
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings
from frobi.shared.infrastructure.llm import DisabledPdfTranscriber, LlmClient, PdfTranscriber

from .auth import current_person_id


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    factory = cast(async_sessionmaker[AsyncSession], request.app.state.session_factory)
    async with factory() as session:
        yield session


def get_redis(request: Request) -> "Redis":
    return cast("Redis", request.app.state.redis)


def get_clock(request: Request) -> Clock:
    return cast(Clock, request.app.state.clock)


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_llm(request: Request) -> LlmClient:
    return cast(LlmClient, request.app.state.llm)


def get_pdf_transcriber(request: Request) -> PdfTranscriber:
    transcriber = getattr(request.app.state, "pdf_transcriber", None)
    return cast(PdfTranscriber, transcriber or DisabledPdfTranscriber())


async def class_context(
    request: Request, person_id: Annotated[UUID, Depends(current_person_id)]
) -> UUID | None:
    """``class_id`` of the person's active class, or None outside any class (RNF16)."""
    context = cast(ClassContext, request.app.state.class_context)
    return await context.active_class(person_id)


CurrentClassId = Annotated[UUID | None, Depends(class_context)]
