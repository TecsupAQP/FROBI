"""M4 y M5 · Adaptación, receta y límites: contract with the front."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.adaptations.application import FormatOption
from frobi.modules.adaptations.domain import Adaptation, Format
from frobi.modules.adaptations.domain import Recipe as DomainRecipe


class FormatOut(BaseModel):
    id: Format
    name: str
    description: str
    icon: str
    suggested: bool = Field(description="Sugerido según los perfiles de la persona.")

    @classmethod
    def from_option(cls, option: FormatOption) -> "FormatOut":
        return cls(
            id=option.info.id,
            name=option.info.name,
            description=option.info.description,
            icon=option.info.icon,
            suggested=option.suggested,
        )


class CreateAdaptationRequest(BaseModel):
    format: Format
    topic: int | None = Field(
        default=None,
        ge=1,
        description="Tema del material (`topics[].position`). Sin él, el primero. La IA solo "
        "lee ese tema, así un PDF largo cuesta lo mismo por petición que uno corto.",
    )


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

    @classmethod
    def from_domain(cls, recipe: DomainRecipe) -> "Recipe":
        return cls(
            context=recipe.context, goal=recipe.goal, level=recipe.level, format=recipe.format
        )


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
    topic: int | None = Field(default=None, description="Tema adaptado (`topics[].position`).")

    @classmethod
    def from_domain(cls, adaptation: Adaptation) -> "AdaptationOut":
        return cls(
            id=adaptation.id,
            material_id=adaptation.material_id,
            format=adaptation.format,
            content=AdaptationContent(
                title=adaptation.content.title,
                sections=[
                    ContentSection(heading=s.heading, body=s.body, items=list(s.items))
                    for s in adaptation.content.sections
                ],
                plain_text=adaptation.content.plain_text(),
            ),
            recipe=Recipe.from_domain(adaptation.recipe),
            prompt_text=adaptation.recipe.prompt_text(),
            ai_notice=adaptation.ai_notice,
            fallback=adaptation.fallback,
            created_at=adaptation.created_at,
            topic=adaptation.topic,
        )
