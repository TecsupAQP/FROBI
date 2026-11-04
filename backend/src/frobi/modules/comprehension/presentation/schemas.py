"""M8 · Verificación: contract with the front."""

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionKind(StrEnum):
    COMPREHENSION = "comprehension"
    TRANSFER = "transfer"


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
