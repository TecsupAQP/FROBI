"""Activity of comprehension for progress and the panel (see shared.application.activity)."""

from uuid import UUID

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import AnswerRow

from .models import AnswerModel, QuestionModel


async def _answers(session: AsyncSession, where: ColumnElement[bool]) -> list[AnswerRow]:
    query = (
        select(
            AnswerModel.person_id,
            AnswerModel.question_id,
            QuestionModel.statement,
            QuestionModel.source_format,
            AnswerModel.is_correct,
            AnswerModel.used_help,
            AnswerModel.created_at,
        )
        .join(QuestionModel, QuestionModel.id == AnswerModel.question_id)
        .where(where)
        .order_by(AnswerModel.created_at)
    )
    return [
        AnswerRow(
            row.person_id,
            row.question_id,
            row.statement,
            row.source_format,
            row.is_correct,
            row.used_help,
            row.created_at,
        )
        for row in await session.execute(query)
    ]


async def answers_in_class(session: AsyncSession, class_id: UUID) -> list[AnswerRow]:
    return await _answers(session, AnswerModel.class_id == class_id)


async def answers_of_person(session: AsyncSession, person_id: UUID) -> list[AnswerRow]:
    return await _answers(session, AnswerModel.person_id == person_id)
