"""M6 · Tutor con escalera de ayuda."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.modules.tutoring.application import (
    GetAttemptHandler,
    OpenAttemptCommand,
    OpenAttemptHandler,
    RequestStepCommand,
    RequestStepHandler,
    SubmitOwnAnswerCommand,
    SubmitOwnAnswerHandler,
)
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentClassId,
    CurrentPersonId,
    problem,
)

from .dependencies import (
    get_get_attempt,
    get_open_attempt,
    get_request_step,
    get_submit_own_answer,
)
from .schemas import (
    HelpAttemptOut,
    OpenAttemptRequest,
    OwnAnswerOut,
    OwnAnswerRequest,
    RequestStepRequest,
    StepOut,
)

router = APIRouter(
    prefix="/help-attempts",
    tags=["M6 · Escalera de ayuda"],
    responses={**AUTH_RESPONSES, **NOT_FOUND_RESPONSES},
)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Abrir un intento sobre una tarea")
async def open_attempt(
    body: OpenAttemptRequest,
    person_id: CurrentPersonId,
    class_id: CurrentClassId,
    handler: Annotated[OpenAttemptHandler, Depends(get_open_attempt)],
) -> HelpAttemptOut:
    attempt = await handler.handle(
        OpenAttemptCommand(
            person_id=person_id,
            class_id=class_id,
            adaptation_id=body.adaptation_id,
            task_ref=body.task_ref,
        )
    )
    return HelpAttemptOut.from_domain(attempt)


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
async def request_step(
    attempt_id: UUID,
    body: RequestStepRequest,
    person_id: CurrentPersonId,
    handler: Annotated[RequestStepHandler, Depends(get_request_step)],
) -> StepOut:
    result = await handler.handle(
        RequestStepCommand(person_id=person_id, attempt_id=attempt_id, step=body.step)
    )
    return StepOut.from_result(result)


@router.post("/{attempt_id}/own-answer", summary="Inténtalo sin IA")
async def submit_own_answer(
    attempt_id: UUID,
    body: OwnAnswerRequest,
    person_id: CurrentPersonId,
    handler: Annotated[SubmitOwnAnswerHandler, Depends(get_submit_own_answer)],
) -> OwnAnswerOut:
    result = await handler.handle(
        SubmitOwnAnswerCommand(
            person_id=person_id,
            attempt_id=attempt_id,
            answer=body.answer,
            self_check=tuple(body.self_check),
        )
    )
    return OwnAnswerOut.from_result(result)


@router.get("/{attempt_id}", summary="Estado del intento y nivel de ayuda")
async def get_attempt(
    attempt_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GetAttemptHandler, Depends(get_get_attempt)],
) -> HelpAttemptOut:
    return HelpAttemptOut.from_domain(await handler.handle(person_id, attempt_id))
