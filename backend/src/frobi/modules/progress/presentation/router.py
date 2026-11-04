"""M11 · Progreso y cierre.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from frobi.shared.presentation import AUTH_RESPONSES, require_token

from .schemas import (
    FormatAccuracy,
    FormatUsage,
    JourneySummaryOut,
    LearnedRecipe,
    ProgressOut,
    PromptScorePoint,
)

router = APIRouter(
    prefix="/me",
    tags=["M11 · Progreso y cierre"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)


@router.get("/progress", summary="Progreso de la persona (o estado vacío explícito)")
async def get_progress() -> ProgressOut:
    return ProgressOut(
        has_data=True,
        formats_used=[
            FormatUsage(format="easy_read", count=3),
            FormatUsage(format="visual_map", count=1),
        ],
        accuracy_by_format=[
            FormatAccuracy(format="easy_read", correct=4, total=5),
            FormatAccuracy(format="visual_map", correct=1, total=2),
        ],
        prompt_scores=[
            PromptScorePoint(at=datetime(2026, 11, 4, 12, 10, tzinfo=UTC), total=6),
            PromptScorePoint(at=datetime(2026, 11, 4, 12, 30, tzinfo=UTC), total=11),
        ],
        solved_without_ai=2,
        message="Aprendes mejor con lectura fácil y tus instrucciones mejoran cada vez.",
    )


@router.get("/journey-summary", summary="Cierre del recorrido")
async def get_journey_summary() -> JourneySummaryOut:
    return JourneySummaryOut(
        favorite_format="easy_read",
        learned_recipe=LearnedRecipe(
            context="Estudiante de Mecatrónica con la guía de sensores.",
            goal="Diferenciar tipos de sensores.",
            level="Primer año.",
            format="easy_read",
        ),
        best_prompt_score=11,
        autonomy_level=2,
        message="Ya sabes pedirle a la IA lo que necesitas y comprobarlo con tu material.",
    )
