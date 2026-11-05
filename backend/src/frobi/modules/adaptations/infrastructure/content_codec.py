"""AdaptedContent <-> JSON, with validation (database, Redis, fallback files and model output)."""

from typing import Any

from pydantic import BaseModel, Field

from frobi.modules.adaptations.domain import AdaptedContent, Recipe, Section


class SectionJson(BaseModel):
    heading: str = Field(min_length=1, max_length=200)
    body: str = Field(default="", max_length=4000)
    items: list[str] = Field(default_factory=list, max_length=20)


class ContentJson(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    sections: list[SectionJson] = Field(min_length=1, max_length=20)


def content_from_json(data: Any) -> AdaptedContent:
    """Raises pydantic.ValidationError if the shape is wrong (e.g. a model that misbehaved)."""
    parsed = ContentJson.model_validate(data)
    return AdaptedContent(
        title=parsed.title,
        sections=tuple(
            Section(heading=s.heading, body=s.body, items=tuple(s.items)) for s in parsed.sections
        ),
    )


def content_to_json(content: AdaptedContent) -> dict[str, Any]:
    return {
        "title": content.title,
        "sections": [
            {"heading": s.heading, "body": s.body, "items": list(s.items)} for s in content.sections
        ],
    }


def recipe_to_json(recipe: Recipe) -> dict[str, str]:
    return {
        "context": recipe.context,
        "goal": recipe.goal,
        "level": recipe.level,
        "format": recipe.format.value,
    }
