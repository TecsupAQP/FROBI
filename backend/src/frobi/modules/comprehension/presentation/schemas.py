"""M8 · Verificación: contract with the front."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.comprehension.domain import Answer, Question, QuestionKind


class QuestionOption(BaseModel):
    id: str = Field(examples=["a"])
    text: str


class QuestionOut(BaseModel):
    """The correct option is never sent before the person answers."""

    id: UUID
    adaptation_id: UUID
    kind: QuestionKind
    statement: str
    options: list[QuestionOption]

    @classmethod
    def from_domain(cls, question: Question) -> "QuestionOut":
        return cls(
            id=question.id,
            adaptation_id=question.adaptation_id,
            kind=question.kind,
            statement=question.statement,
            options=[QuestionOption(id=o.id, text=o.text) for o in question.options],
        )


class AnswerRequest(BaseModel):
    option: str = Field(min_length=1, max_length=8, examples=["b"])


class AnswerOut(BaseModel):
    question_id: UUID
    chosen_option: str
    is_correct: bool
    correct_option: str
    feedback: str
    suggested_format: Literal["visual_map", "real_example", "easy_read", "audio"] | None = Field(
        description="Solo si falla: «Prueba con…» (RF14)."
    )
    used_help: bool

    @classmethod
    def from_domain(cls, answer: Answer) -> "AnswerOut":
        return cls(
            question_id=answer.question_id,
            chosen_option=answer.chosen_option,
            is_correct=answer.verdict.is_correct,
            correct_option=answer.verdict.correct_option,
            feedback=answer.verdict.feedback,
            suggested_format=answer.verdict.suggested_format,  # type: ignore[arg-type]
            used_help=answer.used_help,
        )
