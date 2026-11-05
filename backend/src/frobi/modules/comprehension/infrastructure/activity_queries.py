"""Activity of comprehension for progress and the panel (see shared.application.activity)."""

from uuid import UUID

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import AnswerRow, QuestionResult

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


async def question_results(
    session: AsyncSession, adaptation_ids: list[UUID]
) -> list[QuestionResult]:
    """Questions over these adaptations, each with its person's latest answer (if any)."""
    if not adaptation_ids:
        return []
    questions = (
        await session.execute(
            select(QuestionModel.id, QuestionModel.person_id, QuestionModel.adaptation_id).where(
                QuestionModel.adaptation_id.in_(adaptation_ids)
            )
        )
    ).all()
    latest: dict[UUID, bool] = {}
    answers = await session.execute(
        select(AnswerModel.question_id, AnswerModel.is_correct)
        .where(AnswerModel.question_id.in_([q.id for q in questions]))
        .order_by(AnswerModel.created_at)
    )
    for answer in answers:
        latest[answer.question_id] = answer.is_correct
    return [
        QuestionResult(q.person_id, q.adaptation_id, q.id, q.id in latest, latest.get(q.id, False))
        for q in questions
    ]
