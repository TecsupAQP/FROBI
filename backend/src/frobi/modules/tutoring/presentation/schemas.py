"""M6 · Tutor con escalera de ayuda: contract with the front."""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.tutoring.application import OwnAnswerResult, StepResult
from frobi.modules.tutoring.domain import HelpAttempt, HelpStep, ReachedStep


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

    @classmethod
    def from_domain(cls, attempt: HelpAttempt) -> "HelpAttemptOut":
        return cls(
            id=attempt.id,
            adaptation_id=attempt.adaptation_id,
            task_ref=attempt.task_ref,
            max_step=attempt.max_step,
            next_step=attempt.next_step,
            final_unlocked=attempt.final_unlocked,
            own_answer_submitted=attempt.own_answer is not None,
            solved_without_ai=attempt.solved_without_ai,
            help_level=attempt.help_level,
            help_label=attempt.help_label,
        )


class StepOut(BaseModel):
    attempt: HelpAttemptOut
    step: HelpStep
    content: str
    fallback: bool

    @classmethod
    def from_result(cls, result: StepResult) -> "StepOut":
        return cls(
            attempt=HelpAttemptOut.from_domain(result.attempt),
            step=result.step,
            content=result.content,
            fallback=result.fallback,
        )


class GuidePassage(BaseModel):
    text: str
    location: str = Field(examples=["«Guía de sensores», Sensores inductivos, párrafo 1"])


class OwnAnswerOut(BaseModel):
    attempt: HelpAttemptOut
    matching_passages: list[GuidePassage] = Field(
        description="Pasajes de la guía que coinciden con tu respuesta. Se buscan sin IA."
    )

    @classmethod
    def from_result(cls, result: OwnAnswerResult) -> "OwnAnswerOut":
        return cls(
            attempt=HelpAttemptOut.from_domain(result.attempt),
            matching_passages=[
                GuidePassage(text=p.text, location=p.location) for p in result.matching_passages
            ],
        )
