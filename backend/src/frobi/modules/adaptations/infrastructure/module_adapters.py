"""Adaptations' ports over the public APIs of materials and settings."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import materials, settings
from frobi.modules.adaptations.application.ports import ProfileView, SourceMaterial


class MaterialReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._get = materials.get_material_handler(session)

    async def find(self, person_id: UUID, material_id: UUID) -> SourceMaterial | None:
        material = await self._get.find(person_id, material_id)
        if material is None:
            return None
        return SourceMaterial(id=material.id, title=material.title, text=material.text)


class ProfileReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._get = settings.get_settings_handler(session)

    async def for_person(self, person_id: UUID) -> ProfileView:
        stored = await self._get.handle(person_id)
        return ProfileView(enabled_settings=frozenset(stored.enabled))
