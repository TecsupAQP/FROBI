"""A material and its text, for whoever may see it. Also part of the public API (adaptations)."""

from uuid import UUID

from frobi.modules.materials.application.ports import MaterialRepository, SampleCatalog
from frobi.modules.materials.domain import Material, MaterialNotFound


class GetMaterialHandler:
    def __init__(self, materials: MaterialRepository, samples: SampleCatalog) -> None:
        self._materials = materials
        self._samples = samples

    async def find(self, person_id: UUID, material_id: UUID) -> Material | None:
        material = self._samples.get(material_id) or await self._materials.get(material_id)
        if material is None or not material.visible_to(person_id):
            return None
        return material

    async def handle(self, person_id: UUID, material_id: UUID) -> Material:
        material = await self.find(person_id, material_id)
        if material is None:
            raise MaterialNotFound()
        return material
