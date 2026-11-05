"""Activity of tutoring for progress and the teacher panel (see shared.application.activity)."""

from uuid import UUID

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import HelpUse, TaskAttempt

from .models import HelpAttemptModel


async def _uses(session: AsyncSession, where: ColumnElement[bool]) -> list[HelpUse]:
    query = select(
        HelpAttemptModel.person_id,
        HelpAttemptModel.max_step,
        HelpAttemptModel.own_answer.is_not(None).label("own_answer"),
        HelpAttemptModel.solved_without_ai,
    ).where(where)
    return [
        HelpUse(row.person_id, row.max_step, bool(row.own_answer), row.solved_without_ai)
        for row in await session.execute(query)
    ]


async def help_in_class(session: AsyncSession, class_id: UUID) -> list[HelpUse]:
    return await _uses(session, HelpAttemptModel.class_id == class_id)


async def help_of_person(session: AsyncSession, person_id: UUID) -> list[HelpUse]:
    return await _uses(session, HelpAttemptModel.person_id == person_id)


async def task_attempts_in_class(session: AsyncSession, class_id: UUID) -> list[TaskAttempt]:
    """Attempts on the tasks of the class guides (``task_ref`` «tarea-…»)."""
    query = select(
        HelpAttemptModel.person_id,
        HelpAttemptModel.task_ref,
        HelpAttemptModel.own_answer.is_not(None).label("own_answer"),
    ).where(HelpAttemptModel.class_id == class_id, HelpAttemptModel.task_ref.like("tarea-%"))
    return [
        TaskAttempt(row.person_id, row.task_ref, bool(row.own_answer))
        for row in await session.execute(query)
    ]
