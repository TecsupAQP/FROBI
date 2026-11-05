"""Public API of prompt_coach: the only thing other modules' adapters may import."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import PromptScoreRow


async def scores_in_class(session: AsyncSession, class_id: UUID) -> list[PromptScoreRow]:
    """Prompt evaluations made inside this class only (RNF16)."""
    from .infrastructure.activity_queries import scores_in_class as query

    return await query(session, class_id)


async def scores_of_person(session: AsyncSession, person_id: UUID) -> list[PromptScoreRow]:
    from .infrastructure.activity_queries import scores_of_person as query

    return await query(session, person_id)


__all__ = ["scores_in_class", "scores_of_person"]
