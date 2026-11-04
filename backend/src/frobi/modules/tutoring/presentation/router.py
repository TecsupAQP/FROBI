"""M6 · Tutor con escalera de ayuda.

Stub: returns example data so the front can integrate. The real use cases replace each body.
The stub keeps no state: it opens hint_1, hint_2 and step_by_step, and always locks `final`
so the front can render that 409.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.modules.tutoring.domain.errors import FinalLocked
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    problem,
    require_token,
)

from .schemas import (
    GuidePassage,
    HelpAttemptOut,
    HelpStep,
    OpenAttemptRequest,
    OwnAnswerOut,
    OwnAnswerRequest,
    ReachedStep,
    RequestStepRequest,
    StepOut,
)

router = APIRouter(
    prefix="/help-attempts",
    tags=["M6 · Escalera de ayuda"],
    dependencies=[Depends(require_token)],
    responses={**AUTH_RESPONSES, **NOT_FOUND_RESPONSES},
)

EXAMPLE_ATTEMPT_ID = UUID("00000000-0000-4000-8000-00000000e001")
EXAMPLE_ADAPTATION_ID = UUID("00000000-0000-4000-8000-00000000d001")

_ORDER = [HelpStep.HINT_1, HelpStep.HINT_2, HelpStep.STEP_BY_STEP, HelpStep.FINAL]
_LABELS = {
    ReachedStep.NONE: "Nivel 0, sin ayuda",
    ReachedStep.HINT_1: "Nivel 1, con una pista",
    ReachedStep.HINT_2: "Nivel 2, con pistas",
    ReachedStep.STEP_BY_STEP: "Nivel 3, paso a paso",
    ReachedStep.FINAL: "Nivel 4, con la respuesta",
}
_CONTENT = {
    HelpStep.HINT_1: "Piensa en qué material tiene la pieza que quieres detectar.",
    HelpStep.HINT_2: "La guía dice qué sensor detecta metales y cuál detecta plásticos.",
    HelpStep.STEP_BY_STEP: (
        "1. Mira de qué está hecha la pieza. 2. Busca en la guía qué sensor la detecta. "
        "3. Revisa si necesita contacto."
    ),
}


def _attempt(
    attempt_id: UUID,
    adaptation_id: UUID,
    task_ref: str,
    reached: ReachedStep,
    *,
    own_answer: bool = False,
    solved_without_ai: bool = False,
) -> HelpAttemptOut:
    level = list(ReachedStep).index(reached)
    next_step = _ORDER[level] if level < len(_ORDER) else None
    return HelpAttemptOut(
        id=attempt_id,
        adaptation_id=adaptation_id,
        task_ref=task_ref,
        max_step=reached,
        next_step=next_step,
        final_unlocked=own_answer,
        own_answer_submitted=own_answer,
        solved_without_ai=solved_without_ai,
        help_level=level,
        help_label=_LABELS[reached],
    )


@router.post("", status_code=status.HTTP_201_CREATED, summary="Abrir un intento sobre una tarea")
async def open_attempt(body: OpenAttemptRequest) -> HelpAttemptOut:
    return _attempt(EXAMPLE_ATTEMPT_ID, body.adaptation_id, body.task_ref, ReachedStep.NONE)


@router.post(
    "/{attempt_id}/steps",
    summary="Abrir el siguiente escalón de ayuda",
    responses={
        409: problem(
            "`Tutoring.StepOutOfOrder` si se salta un escalón; "
            "`Tutoring.FinalLocked` si se pide `final` sin intento propio."
        )
    },
)
async def request_step(attempt_id: UUID, body: RequestStepRequest) -> StepOut:
    if body.step is HelpStep.FINAL:
        raise FinalLocked()
    reached = ReachedStep(body.step.value)
    return StepOut(
        attempt=_attempt(attempt_id, EXAMPLE_ADAPTATION_ID, "ejercicio-1", reached),
        step=body.step,
        content=_CONTENT[body.step],
        fallback=False,
    )


@router.post("/{attempt_id}/own-answer", summary="Inténtalo sin IA")
async def submit_own_answer(attempt_id: UUID, body: OwnAnswerRequest) -> OwnAnswerOut:
    return OwnAnswerOut(
        attempt=_attempt(
            attempt_id,
            EXAMPLE_ADAPTATION_ID,
            "ejercicio-1",
            ReachedStep.NONE,
            own_answer=True,
            solved_without_ai=True,
        ),
        matching_passages=[
            GuidePassage(
                text="Los sensores inductivos detectan metales sin contacto.",
                location="Guía de sensores, párrafo 2",
            )
        ],
    )


@router.get("/{attempt_id}", summary="Estado del intento y nivel de ayuda")
async def get_attempt(attempt_id: UUID) -> HelpAttemptOut:
    return _attempt(attempt_id, EXAMPLE_ADAPTATION_ID, "ejercicio-1", ReachedStep.HINT_2)
