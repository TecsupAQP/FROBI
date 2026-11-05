"""M7 · Entrenador de instrucciones."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.modules.prompt_coach.application import (
    ComparePromptsHandler,
    EvaluatePromptCommand,
    EvaluatePromptHandler,
)
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentClassId,
    CurrentPersonId,
)

from .dependencies import get_compare_prompts, get_evaluate_prompt
from .schemas import EvaluatePromptRequest, PromptComparisonOut, PromptEvaluationOut

router = APIRouter(
    prefix="/prompt-evaluations",
    tags=["M7 · Entrenador de instrucciones"],
    responses=AUTH_RESPONSES,
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Puntuar una instrucción",
    responses=NOT_FOUND_RESPONSES,
)
async def evaluate_prompt(
    body: EvaluatePromptRequest,
    person_id: CurrentPersonId,
    class_id: CurrentClassId,
    handler: Annotated[EvaluatePromptHandler, Depends(get_evaluate_prompt)],
) -> PromptEvaluationOut:
    evaluation = await handler.handle(
        EvaluatePromptCommand(
            person_id=person_id,
            class_id=class_id,
            text=body.text,
            material_id=body.material_id,
            claim_id=body.claim_id,
        )
    )
    return PromptEvaluationOut.from_domain(evaluation)


@router.post(
    "/{evaluation_id}/compare",
    summary="Correr la original y la mejorada, lado a lado",
    responses=NOT_FOUND_RESPONSES,
)
async def compare_prompts(
    evaluation_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[ComparePromptsHandler, Depends(get_compare_prompts)],
) -> PromptComparisonOut:
    return PromptComparisonOut.from_comparison(await handler.handle(person_id, evaluation_id))
