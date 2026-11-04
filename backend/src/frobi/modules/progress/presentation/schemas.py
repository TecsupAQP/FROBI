"""M11 · Progreso y cierre: contract with the front."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FormatName = Literal["visual_map", "real_example", "easy_read", "audio"]


class FormatUsage(BaseModel):
    format: FormatName
    count: int = Field(ge=0)


class FormatAccuracy(BaseModel):
    format: FormatName
    correct: int = Field(ge=0)
    total: int = Field(ge=0)


class PromptScorePoint(BaseModel):
    at: datetime
    total: int = Field(ge=0, le=16, description="Suma de las 4 piezas (0 a 4 cada una).")


class ProgressOut(BaseModel):
    has_data: bool = Field(description="`false`: estado vacío explícito, mostrar `message`.")
    formats_used: list[FormatUsage]
    accuracy_by_format: list[FormatAccuracy]
    prompt_scores: list[PromptScorePoint]
    solved_without_ai: int = Field(ge=0)
    message: str


class LearnedRecipe(BaseModel):
    context: str
    goal: str
    level: str
    format: FormatName


class JourneySummaryOut(BaseModel):
    favorite_format: FormatName | None
    learned_recipe: LearnedRecipe | None
    best_prompt_score: int | None = Field(ge=0, le=16)
    autonomy_level: int | None = Field(ge=1, le=3)
    message: str
