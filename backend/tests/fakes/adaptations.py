import asyncio
from typing import Any
from uuid import UUID

from frobi.modules.adaptations.application.ports import Generated, ProfileView, SourceMaterial
from frobi.modules.adaptations.domain import Adaptation, AdaptedContent, Recipe, Section

SOURCE = SourceMaterial(
    id=UUID("00000000-0000-4000-8000-0000000000f1"),
    title="Apuntes de sensores",
    text="## Inductivos\nDetectan metales sin contacto.\n## Capacitivos\nDetectan líquidos.",
)

AI_CONTENT = AdaptedContent(
    title="Versión de la IA", sections=(Section("Idea", "Contenido generado"),)
)
VALID_LLM_JSON: dict[str, Any] = {
    "title": "Versión de la IA",
    "sections": [{"heading": "Idea", "body": "Contenido generado", "items": []}],
}


class StaticMaterials:
    def __init__(self, owner: UUID, material: SourceMaterial = SOURCE) -> None:
        self._owner = owner
        self._material = material

    async def find(
        self, person_id: UUID, material_id: UUID, topic: int | None = None
    ) -> SourceMaterial | None:
        if person_id == self._owner and material_id == self._material.id and topic in (None, 1):
            return self._material
        return None


class StaticProfiles:
    def __init__(self, *enabled: str) -> None:
        self._view = ProfileView(enabled_settings=frozenset(enabled))

    async def for_person(self, person_id: UUID) -> ProfileView:
        return self._view


class CountingGenerator:
    def __init__(self, *, fallback: bool = False) -> None:
        self.calls = 0
        self._fallback = fallback

    async def adapt(
        self, *, requested_by: UUID, material: SourceMaterial, recipe: Recipe
    ) -> Generated:
        self.calls += 1
        return Generated(content=AI_CONTENT, fallback=self._fallback)


class InMemoryAdaptations:
    def __init__(self) -> None:
        self.items: dict[UUID, Adaptation] = {}

    async def add(self, adaptation: Adaptation) -> None:
        self.items[adaptation.id] = adaptation

    async def get(self, adaptation_id: UUID) -> Adaptation | None:
        return self.items.get(adaptation_id)


class InMemoryCache:
    def __init__(self) -> None:
        self.values: dict[str, AdaptedContent] = {}
        self.locks: set[str] = set()

    async def get(self, key: str) -> AdaptedContent | None:
        return self.values.get(key)

    async def put(self, key: str, content: AdaptedContent) -> None:
        self.values[key] = content

    async def try_lock(self, key: str) -> bool:
        if key in self.locks:
            return False
        self.locks.add(key)
        return True

    async def unlock(self, key: str) -> None:
        self.locks.discard(key)


class ScriptedLlm:
    """LLM double: answers ``reply`` after ``delay`` seconds, or raises ``error``."""

    def __init__(
        self,
        reply: dict[str, Any] | None = None,
        *,
        delay: float = 0.0,
        error: Exception | None = None,
    ) -> None:
        self.reply = reply if reply is not None else VALID_LLM_JSON
        self.delay = delay
        self.error = error
        self.calls = 0

    async def complete_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        self.calls += 1
        await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return self.reply


class Limiter:
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed

    async def allow(self, person_id: UUID) -> bool:
        return self.allowed
