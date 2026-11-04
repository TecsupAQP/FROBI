"""M6 · Tutor con escalera de ayuda: contract with the front."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class HelpStep(StrEnum):
    HINT_1 = "hint_1"
    HINT_2 = "hint_2"
    STEP_BY_STEP = "step_by_step"
    FINAL = "final"


class ReachedStep(StrEnum):
    NONE = "none"
    HINT_1 = "hint_1"
    HINT_2 = "hint_2"
    STEP_BY_STEP = "step_by_step"
    FINAL = "final"


class OpenAttemptRequest(BaseModel):
    adaptation_id: UUID
    task_ref: str = Field(min_length=1, max_length=120, examples=["ejercicio-1"])


class RequestStepRequest(BaseModel):
    step: HelpStep = Field(description="Solo se puede abrir el siguiente escalón.")


class OwnAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=5_000)
    self_check: list[str] = Field(
        default_factory=list, max_length=10, description="Casillas de autochequeo marcadas."
    )


class HelpAttemptOut(BaseModel):
    id: UUID
    adaptation_id: UUID
    task_ref: str
    max_step: ReachedStep
    next_step: HelpStep | None = Field(description="El único escalón que se puede abrir ahora.")
    final_unlocked: bool
    own_answer_submitted: bool
    solved_without_ai: bool
    help_level: int = Field(ge=0, le=4)
    help_label: str = Field(examples=["Nivel 2, con pistas"])


class StepOut(BaseModel):
    attempt: HelpAttemptOut
    step: HelpStep
    content: str
    fallback: bool


class GuidePassage(BaseModel):
    text: str
    location: str = Field(examples=["Guía de sensores, párrafo 2"])


class OwnAnswerOut(BaseModel):
    attempt: HelpAttemptOut
    matching_passages: list[GuidePassage] = Field(
        description="Pasajes de la guía que coinciden con tu respuesta. Se buscan sin IA."
    )
