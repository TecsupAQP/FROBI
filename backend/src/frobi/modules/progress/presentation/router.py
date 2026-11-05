"""M11 · Progreso y cierre: the person's own activity, inside or outside a class."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.progress.application import GetJourneySummaryHandler, GetProgressHandler
from frobi.modules.progress.infrastructure import PersonActivityReaderAdapter
from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId, get_db_session

from .schemas import (
    FormatAccuracy,
    FormatUsage,
    JourneySummaryOut,
    LearnedRecipe,
    ProgressOut,
    PromptScorePoint,
)

router = APIRouter(prefix="/me", tags=["M11 · Progreso y cierre"], responses=AUTH_RESPONSES)


def get_reader(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PersonActivityReaderAdapter:
    return PersonActivityReaderAdapter(db)


Reader = Annotated[PersonActivityReaderAdapter, Depends(get_reader)]


@router.get("/progress", summary="Progreso de la persona (o estado vacío explícito)")
async def get_progress(person_id: CurrentPersonId, reader: Reader) -> ProgressOut:
    progress = await GetProgressHandler(reader).handle(person_id)
    return ProgressOut(
        has_data=progress.has_data,
        formats_used=[FormatUsage(format=f, count=n) for f, n in progress.formats_used],  # type: ignore[arg-type]
        accuracy_by_format=[
            FormatAccuracy(format=a.format, correct=a.correct, total=a.total)  # type: ignore[arg-type]
            for a in progress.accuracy_by_format
        ],
        prompt_scores=[PromptScorePoint(at=at, total=t) for at, t in progress.prompt_scores],
        solved_without_ai=progress.solved_without_ai,
        message=progress.message,
    )


@router.get("/journey-summary", summary="Cierre del recorrido")
async def get_journey_summary(person_id: CurrentPersonId, reader: Reader) -> JourneySummaryOut:
    summary = await GetJourneySummaryHandler(reader).handle(person_id)
    recipe = summary.learned_recipe
    return JourneySummaryOut(
        favorite_format=summary.favorite_format,  # type: ignore[arg-type]
        learned_recipe=None
        if recipe is None
        else LearnedRecipe(
            context=recipe.context,
            goal=recipe.goal,
            level=recipe.level,
            format=recipe.format,  # type: ignore[arg-type]
        ),
        best_prompt_score=summary.best_prompt_score,
        autonomy_level=summary.autonomy_level,
        message=summary.message,
    )
