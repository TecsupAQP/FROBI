"""What prompt_coach needs, in its own words. Adapters live in prompt_coach/infrastructure."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.prompt_coach.domain import PromptEvaluation, RecipePiece


@dataclass(frozen=True, slots=True)
class MaterialContext:
    title: str
    text: str


class MaterialLookup(Protocol):
    """Over the public API of materials: only materials the person may see."""

    async def find(self, person_id: UUID, material_id: UUID) -> MaterialContext | None: ...


@dataclass(frozen=True, slots=True)
class ScoreDraft:
    scores: dict[RecipePiece, int]
    feedback: dict[RecipePiece, str]
    improved_text: str


class PromptScorer(Protocol):
    """Scores the 4 pieces and proposes an improved prompt. Never waits more than the AI cap."""

    async def score(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> ScoreDraft: ...


@dataclass(frozen=True, slots=True)
class RunOutput:
    text: str
    fallback: bool


class PromptRunner(Protocol):
    """Runs a prompt (optionally over a material) to show what it produces (RF11)."""

    async def run(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> RunOutput: ...


class EvaluationRepository(Protocol):
    async def add(self, evaluation: PromptEvaluation) -> None: ...

    async def get(self, evaluation_id: UUID) -> PromptEvaluation | None: ...


__all__ = [
    "EvaluationRepository",
    "MaterialContext",
    "MaterialLookup",
    "PromptRunner",
    "PromptScorer",
    "RunOutput",
    "ScoreDraft",
]
