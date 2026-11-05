"""Adaptations' ports over the public APIs of materials and settings."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import materials, settings
from frobi.modules.adaptations.application.ports import ProfileView, SourceMaterial


class MaterialReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._get = materials.get_material_handler(session)

    async def find(
        self, person_id: UUID, material_id: UUID, topic: int | None = None
    ) -> SourceMaterial | None:
        material = await self._get.find(person_id, material_id)
        found = None if material is None else material.topic(topic)
        if material is None or found is None:
            return None
        several = len(material.topics()) > 1
        return SourceMaterial(
            id=material.id,
            title=f"{material.title} · {found.title}" if several else material.title,
            text=found.text,
            topic=found.position,
        )


class ProfileReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._get = settings.get_settings_handler(session)

    async def for_person(self, person_id: UUID) -> ProfileView:
        stored = await self._get.handle(person_id)
        return ProfileView(enabled_settings=frozenset(stored.enabled))
