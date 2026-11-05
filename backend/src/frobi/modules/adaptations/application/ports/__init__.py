"""What adaptations needs, in its own words. Adapters live in adaptations/infrastructure."""

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID

from frobi.modules.adaptations.domain import Adaptation, AdaptedContent, Recipe


@dataclass(frozen=True, slots=True)
class SourceMaterial:
    id: UUID
    title: str
    text: str


class MaterialReader(Protocol):
    """Over the public API of materials: only materials the person may see."""

    async def find(self, person_id: UUID, material_id: UUID) -> SourceMaterial | None: ...


@dataclass(frozen=True, slots=True)
class ProfileView:
    enabled_settings: frozenset[str] = field(default_factory=frozenset)


class ProfileReader(Protocol):
    """Over the public API of settings."""

    async def for_person(self, person_id: UUID) -> ProfileView: ...


@dataclass(frozen=True, slots=True)
class Generated:
    content: AdaptedContent
    fallback: bool


class TextGenerator(Protocol):
    """Adapts a material following a recipe. Never waits more than the AI time cap."""

    async def adapt(
        self, *, requested_by: UUID, material: SourceMaterial, recipe: Recipe
    ) -> Generated: ...


class AdaptationRepository(Protocol):
    async def add(self, adaptation: Adaptation) -> None: ...

    async def get(self, adaptation_id: UUID) -> Adaptation | None: ...


class AdaptationCache(Protocol):
    """``adapt:{key}`` for 24 h, and ``lock:adapt:{key}`` for 20 s against double clicks."""

    async def get(self, key: str) -> AdaptedContent | None: ...

    async def put(self, key: str, content: AdaptedContent) -> None: ...

    async def try_lock(self, key: str) -> bool: ...

    async def unlock(self, key: str) -> None: ...


__all__ = [
    "AdaptationCache",
    "AdaptationRepository",
    "Generated",
    "MaterialReader",
    "ProfileReader",
    "ProfileView",
    "SourceMaterial",
    "TextGenerator",
]
