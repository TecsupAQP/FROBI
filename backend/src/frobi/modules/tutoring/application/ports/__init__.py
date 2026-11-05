"""What tutoring needs, in its own words. Adapters live in tutoring/infrastructure."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.tutoring.domain import HelpAttempt, HelpStep


@dataclass(frozen=True, slots=True)
class TutoringContext:
    adaptation_id: UUID
    material_title: str
    material_text: str
    adapted_text: str


class TutoringContextReader(Protocol):
    """Over the public APIs of adaptations and materials; only what the person may see."""

    async def get(self, person_id: UUID, adaptation_id: UUID) -> TutoringContext | None: ...


@dataclass(frozen=True, slots=True)
class Hint:
    text: str
    fallback: bool


class HintGenerator(Protocol):
    """Writes the help for one step. Never waits more than the AI time cap."""

    async def hint(
        self, *, requested_by: UUID, context: TutoringContext, task_ref: str, step: HelpStep
    ) -> Hint: ...


class HelpAttemptRepository(Protocol):
    async def add(self, attempt: HelpAttempt) -> None: ...

    async def get(self, attempt_id: UUID, *, for_update: bool = False) -> HelpAttempt | None:
        """``for_update`` locks the row until commit, so two clicks cannot both advance."""
        ...

    async def save(self, attempt: HelpAttempt) -> None: ...


__all__ = [
    "HelpAttemptRepository",
    "Hint",
    "HintGenerator",
    "TutoringContext",
    "TutoringContextReader",
]
