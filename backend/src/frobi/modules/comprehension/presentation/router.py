"""M8 · Verificación."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.modules.comprehension.application import (
    AnswerQuestionCommand,
    AnswerQuestionHandler,
    GenerateQuestionsHandler,
)
from frobi.modules.comprehension.domain import QuestionKind
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentClassId,
    CurrentPersonId,
    problem,
)

from .dependencies import get_answer_question, get_generate_questions
from .schemas import AnswerOut, AnswerRequest, QuestionOut

router = APIRouter(
    tags=["M8 · Verificación"],
    responses={**AUTH_RESPONSES, **NOT_FOUND_RESPONSES},
)


@router.post(
    "/adaptations/{adaptation_id}/questions",
    status_code=status.HTTP_201_CREATED,
    summary="Generar 2 o 3 preguntas sobre el material",
    responses={422: problem("Material demasiado corto (`Comprehension.NotEnoughMaterial`).")},
)
async def generate_questions(
    adaptation_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GenerateQuestionsHandler, Depends(get_generate_questions)],
) -> list[QuestionOut]:
    questions = await handler.handle(person_id, adaptation_id, QuestionKind.COMPREHENSION)
    return [QuestionOut.from_domain(q) for q in questions]


@router.post(
    "/questions/{question_id}/answers",
    summary="Responder una pregunta",
    responses={422: problem("Opción inexistente (`Comprehension.InvalidOption`).")},
)
async def answer_question(
    question_id: UUID,
    body: AnswerRequest,
    person_id: CurrentPersonId,
    class_id: CurrentClassId,
    handler: Annotated[AnswerQuestionHandler, Depends(get_answer_question)],
) -> AnswerOut:
    answer = await handler.handle(
        AnswerQuestionCommand(
            person_id=person_id, class_id=class_id, question_id=question_id, option=body.option
        )
    )
    return AnswerOut.from_domain(answer)


@router.post(
    "/adaptations/{adaptation_id}/transfer-question",
    status_code=status.HTTP_201_CREATED,
    summary="Pregunta similar sin ayuda",
    responses={422: problem("Material demasiado corto (`Comprehension.NotEnoughMaterial`).")},
)
async def transfer_question(
    adaptation_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GenerateQuestionsHandler, Depends(get_generate_questions)],
) -> QuestionOut:
    questions = await handler.handle(person_id, adaptation_id, QuestionKind.TRANSFER)
    return QuestionOut.from_domain(questions[0])
