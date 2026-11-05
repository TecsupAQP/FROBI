"""What comprehension needs, in its own words. Adapters live in comprehension/infrastructure."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.comprehension.domain import Answer, Question, QuestionDraft, QuestionKind


@dataclass(frozen=True, slots=True)
class QuizContext:
    adaptation_id: UUID
    material_id: UUID
    material_title: str
    material_text: str
    format: str


class QuizContextReader(Protocol):
    """Over the public APIs of adaptations and materials; only what the person may see."""

    async def get(self, person_id: UUID, adaptation_id: UUID) -> QuizContext | None: ...


class QuestionGenerator(Protocol):
    """Writes ``n`` questions of a kind. ``skip`` asks for different ones than before."""

    async def generate(
        self,
        *,
        requested_by: UUID,
        context: QuizContext,
        kind: QuestionKind,
        n: int,
        skip: int = 0,
    ) -> list[QuestionDraft]: ...


class QuestionRepository(Protocol):
    async def add_all(self, questions: list[Question]) -> None: ...

    async def get(self, question_id: UUID) -> Question | None: ...

    async def count(self, adaptation_id: UUID, kind: QuestionKind) -> int: ...


class AnswerRepository(Protocol):
    async def add(self, answer: Answer) -> None: ...


__all__ = [
    "AnswerRepository",
    "QuestionGenerator",
    "QuestionRepository",
    "QuizContext",
    "QuizContextReader",
]
