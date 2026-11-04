"""M4 y M5 · Adaptación, receta y límites: contract with the front."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class Format(StrEnum):
    VISUAL_MAP = "visual_map"
    REAL_EXAMPLE = "real_example"
    EASY_READ = "easy_read"
    AUDIO = "audio"


class FormatOut(BaseModel):
    id: Format
    name: str
    description: str
    icon: str
    suggested: bool = Field(description="Sugerido según los perfiles de la persona.")


class CreateAdaptationRequest(BaseModel):
    format: Format


class ContentSection(BaseModel):
    heading: str
    body: str
    items: list[str] = Field(default_factory=list)


class AdaptationContent(BaseModel):
    title: str
    sections: list[ContentSection]
    plain_text: str = Field(description="Texto continuo; en `audio` lo lee la voz del navegador.")


class Recipe(BaseModel):
    """The 4-piece recipe shown to the person (RF07) is the same one sent to the model."""

    context: str
    goal: str
    level: str
    format: Format


class AdaptationOut(BaseModel):
    id: UUID
    material_id: UUID
    format: Format
    content: AdaptationContent
    recipe: Recipe
    prompt_text: str = Field(description="Receta lista para «Copiar receta» (RF08).")
    ai_notice: str = Field(description="Aviso de límites de la IA (RF30).")
    fallback: bool = Field(description="`true` si se usó la respuesta de respaldo (RF29).")
    created_at: datetime
