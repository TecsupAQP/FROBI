"""M7 · Entrenador de instrucciones.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.shared.presentation import AUTH_RESPONSES, NOT_FOUND_RESPONSES, require_token

from .schemas import (
    EvaluatePromptRequest,
    PieceScore,
    PromptComparisonOut,
    PromptEvaluationOut,
    PromptRun,
    RecipePiece,
)

router = APIRouter(
    prefix="/prompt-evaluations",
    tags=["M7 · Entrenador de instrucciones"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

EXAMPLE_EVALUATION_ID = UUID("00000000-0000-4000-8000-00000000f001")
IMPROVED = (
    "Soy estudiante de primer año de Mecatrónica. Con la guía de sensores, explícame la "
    "diferencia entre un sensor inductivo y uno capacitivo en una tabla de dos columnas."
)


@router.post("", status_code=status.HTTP_201_CREATED, summary="Puntuar una instrucción")
async def evaluate_prompt(body: EvaluatePromptRequest) -> PromptEvaluationOut:
    return PromptEvaluationOut(
        id=EXAMPLE_EVALUATION_ID,
        text=body.text,
        scores=[
            PieceScore(piece=RecipePiece.LEVEL, score=0, feedback="No dices qué sabes ya."),
            PieceScore(piece=RecipePiece.FORMAT, score=1, feedback="No dices cómo lo quieres."),
            PieceScore(piece=RecipePiece.CONTEXT, score=2, feedback="Mencionas el tema."),
            PieceScore(piece=RecipePiece.GOAL, score=3, feedback="Se entiende qué buscas."),
        ],
        missing_piece=RecipePiece.LEVEL,
        suggestion="Cuenta tu nivel: por ejemplo, «soy de primer año».",
        improved_text=IMPROVED,
        autonomy_level=2,
        autonomy_label="Nivel 2: ya pides con contexto",
    )


@router.post(
    "/{evaluation_id}/compare",
    summary="Correr la original y la mejorada, lado a lado",
    responses=NOT_FOUND_RESPONSES,
)
async def compare_prompts(evaluation_id: UUID) -> PromptComparisonOut:
    return PromptComparisonOut(
        evaluation_id=evaluation_id,
        original=PromptRun(
            prompt="explicame sensores",
            output="Un sensor es un dispositivo que detecta cambios en el entorno…",
        ),
        improved=PromptRun(
            prompt=IMPROVED,
            output="| Inductivo | Capacitivo |\n| Detecta metales | Detecta metales, "
            "plásticos y líquidos |",
        ),
        fallback=False,
    )
