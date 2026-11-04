"""M8 · Verificación.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.shared.presentation import AUTH_RESPONSES, NOT_FOUND_RESPONSES, require_token

from .schemas import AnswerOut, AnswerRequest, QuestionKind, QuestionOption, QuestionOut

router = APIRouter(
    tags=["M8 · Verificación"],
    dependencies=[Depends(require_token)],
    responses={**AUTH_RESPONSES, **NOT_FOUND_RESPONSES},
)

QUESTION_1 = UUID("00000000-0000-4000-8000-000000001001")
QUESTION_2 = UUID("00000000-0000-4000-8000-000000001002")
TRANSFER_QUESTION = UUID("00000000-0000-4000-8000-000000001003")
CORRECT_OPTION = "b"


@router.post(
    "/adaptations/{adaptation_id}/questions",
    status_code=status.HTTP_201_CREATED,
    summary="Generar 2 o 3 preguntas sobre el material",
)
async def generate_questions(adaptation_id: UUID) -> list[QuestionOut]:
    return [
        QuestionOut(
            id=QUESTION_1,
            adaptation_id=adaptation_id,
            kind=QuestionKind.COMPREHENSION,
            statement="¿Qué sensor detecta una botella de plástico?",
            options=[
                QuestionOption(id="a", text="Inductivo"),
                QuestionOption(id="b", text="Capacitivo"),
                QuestionOption(id="c", text="Termopar"),
            ],
        ),
        QuestionOut(
            id=QUESTION_2,
            adaptation_id=adaptation_id,
            kind=QuestionKind.COMPREHENSION,
            statement="¿Qué convierte un sensor?",
            options=[
                QuestionOption(id="a", text="Energía eléctrica en movimiento"),
                QuestionOption(id="b", text="Una magnitud física en una señal eléctrica"),
                QuestionOption(id="c", text="Calor en presión"),
            ],
        ),
    ]


@router.post("/questions/{question_id}/answers", summary="Responder una pregunta")
async def answer_question(question_id: UUID, body: AnswerRequest) -> AnswerOut:
    correct = body.option == CORRECT_OPTION
    return AnswerOut(
        question_id=question_id,
        chosen_option=body.option,
        is_correct=correct,
        correct_option=CORRECT_OPTION,
        feedback=(
            "¡Bien! El capacitivo detecta también plásticos."
            if correct
            else "El inductivo solo detecta metales. Revisa la parte de tipos de sensores."
        ),
        suggested_format=None if correct else "visual_map",
        used_help=question_id != TRANSFER_QUESTION,
    )


@router.post(
    "/adaptations/{adaptation_id}/transfer-question",
    status_code=status.HTTP_201_CREATED,
    summary="Pregunta similar sin ayuda",
)
async def transfer_question(adaptation_id: UUID) -> QuestionOut:
    return QuestionOut(
        id=TRANSFER_QUESTION,
        adaptation_id=adaptation_id,
        kind=QuestionKind.TRANSFER,
        statement="En una línea de envasado de jugo, ¿qué sensor usarías para detectar el nivel?",
        options=[
            QuestionOption(id="a", text="Inductivo"),
            QuestionOption(id="b", text="Capacitivo"),
            QuestionOption(id="c", text="Ninguno"),
        ],
    )
