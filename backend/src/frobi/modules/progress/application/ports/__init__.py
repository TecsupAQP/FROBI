"""What progress needs. It owns no table: it only reads the other modules (like ``alerts`` in
famas), through their public APIs."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.shared.application import AnswerRow, FormatUse, HelpUse, PromptScoreRow


@dataclass(frozen=True, slots=True)
class RecipeView:
    context: str
    goal: str
    level: str
    format: str


@dataclass(frozen=True, slots=True)
class PersonActivity:
    formats: list[FormatUse]
    help: list[HelpUse]
    answers: list[AnswerRow]
    prompt_scores: list[PromptScoreRow]
    latest_recipe: RecipeView | None

    @property
    def empty(self) -> bool:
        return not (self.formats or self.help or self.answers or self.prompt_scores)


class PersonActivityReader(Protocol):
    async def read(self, person_id: UUID) -> PersonActivity: ...


__all__ = ["PersonActivity", "PersonActivityReader", "RecipeView"]
