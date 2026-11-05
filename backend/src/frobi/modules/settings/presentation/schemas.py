"""M13 · Ajustes y privacidad: contract with the front."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.settings.domain import Language, PersonSettings


class SettingsOut(BaseModel):
    profiles: list[str] = Field(description="Ids de `GET /accessibility-profiles`.")
    voice: bool
    high_contrast: bool
    large_text: bool
    short_texts: bool
    captions: bool
    large_buttons: bool
    keyboard_mode: bool
    language: Language

    @classmethod
    def from_domain(cls, settings: PersonSettings) -> "SettingsOut":
        return cls(
            profiles=list(settings.profiles),
            voice=settings.is_on("voice"),
            high_contrast=settings.is_on("high_contrast"),
            large_text=settings.is_on("large_text"),
            short_texts=settings.is_on("short_texts"),
            captions=settings.is_on("captions"),
            large_buttons=settings.is_on("large_buttons"),
            keyboard_mode=settings.is_on("keyboard_mode"),
            language=settings.language,
        )


class SettingsPatch(BaseModel):
    """Only the fields that are sent change."""

    voice: bool | None = None
    high_contrast: bool | None = None
    large_text: bool | None = None
    short_texts: bool | None = None
    captions: bool | None = None
    large_buttons: bool | None = None
    keyboard_mode: bool | None = None
    language: Language | None = Field(default=None, description="Solo `es` está disponible.")


class AliasPatch(BaseModel):
    alias: str = Field(min_length=1, max_length=40)


class AccountOut(BaseModel):
    id: UUID
    alias: str
    career: str
    role: Literal["learner", "teacher"]


class PrivacyItem(BaseModel):
    category: str
    description: str


class PrivacyOut(BaseModel):
    in_class: bool
    class_name: str | None
    shared_with_teacher: list[PrivacyItem] = Field(
        description="Solo lo hecho dentro de la clase, con el `class_id` de esa clase."
    )
    never_shared: list[PrivacyItem]


class LanguageOut(BaseModel):
    code: Language
    name: str
    status: Literal["available", "coming_soon"]
