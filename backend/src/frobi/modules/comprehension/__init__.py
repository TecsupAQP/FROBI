"""Public API of comprehension: the only thing other modules' adapters may import."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import AnswerRow


async def answers_in_class(session: AsyncSession, class_id: UUID) -> list[AnswerRow]:
    """Answers given inside this class only (RNF16)."""
    from .infrastructure.activity_queries import answers_in_class as query

    return await query(session, class_id)


async def answers_of_person(session: AsyncSession, person_id: UUID) -> list[AnswerRow]:
    from .infrastructure.activity_queries import answers_of_person as query

    return await query(session, person_id)


__all__ = ["answers_in_class", "answers_of_person"]
