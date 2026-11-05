"""Public API of tutoring: the only thing other modules' adapters may import."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import HelpUse, TaskAttempt


async def help_in_class(session: AsyncSession, class_id: UUID) -> list[HelpUse]:
    """Help attempts made inside this class only (RNF16)."""
    from .infrastructure.activity_queries import help_in_class as query

    return await query(session, class_id)


async def help_of_person(session: AsyncSession, person_id: UUID) -> list[HelpUse]:
    from .infrastructure.activity_queries import help_of_person as query

    return await query(session, person_id)


async def task_attempts_in_class(session: AsyncSession, class_id: UUID) -> list[TaskAttempt]:
    """Attempts on the tasks of this class's guides only (RNF16)."""
    from .infrastructure.activity_queries import task_attempts_in_class as query

    return await query(session, class_id)


__all__ = ["help_in_class", "help_of_person", "task_attempts_in_class"]
