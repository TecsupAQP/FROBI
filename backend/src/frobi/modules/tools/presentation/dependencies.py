"""Wiring: builds tools' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.tools.application import RecommendToolHandler
from frobi.modules.tools.infrastructure import ClaimLookupAdapter
from frobi.shared.presentation import get_db_session


def get_recommend_tool(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RecommendToolHandler:
    return RecommendToolHandler(ClaimLookupAdapter(db))
