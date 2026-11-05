"""Activity of prompt_coach for progress and the teacher panel (see shared.application.activity)."""

from uuid import UUID

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import PromptScoreRow

from .models import PromptEvaluationModel


async def _scores(session: AsyncSession, where: ColumnElement[bool]) -> list[PromptScoreRow]:
    query = (
        select(
            PromptEvaluationModel.person_id,
            PromptEvaluationModel.total,
            PromptEvaluationModel.autonomy_level,
            PromptEvaluationModel.created_at,
        )
        .where(where)
        .order_by(PromptEvaluationModel.created_at)
    )
    return [
        PromptScoreRow(row.person_id, row.total, row.autonomy_level, row.created_at)
        for row in await session.execute(query)
    ]


async def scores_in_class(session: AsyncSession, class_id: UUID) -> list[PromptScoreRow]:
    return await _scores(session, PromptEvaluationModel.class_id == class_id)


async def scores_of_person(session: AsyncSession, person_id: UUID) -> list[PromptScoreRow]:
    return await _scores(session, PromptEvaluationModel.person_id == person_id)
