"""A material and its text, for whoever may see it. Also part of the public API (adaptations)."""

from uuid import UUID

from frobi.modules.materials.application.ports import MaterialRepository, SampleCatalog
from frobi.modules.materials.domain import Material, MaterialNotFound
from frobi.shared.application import ClassContext


class GetMaterialHandler:
    def __init__(
        self,
        materials: MaterialRepository,
        samples: SampleCatalog,
        classes: ClassContext | None = None,
    ) -> None:
        """Without ``classes`` nobody reads class content except the teacher who uploaded it."""
        self._materials = materials
        self._samples = samples
        self._classes = classes

    async def find(self, person_id: UUID, material_id: UUID) -> Material | None:
        material = self._samples.get(material_id) or await self._materials.get(material_id)
        if material is None:
            return None
        if material.visible_to(person_id):
            return material
        if material.class_id is None or self._classes is None:
            return None
        active = await self._classes.active_class(person_id)
        return material if material.visible_to(person_id, active) else None

    async def handle(self, person_id: UUID, material_id: UUID) -> Material:
        material = await self.find(person_id, material_id)
        if material is None:
            raise MaterialNotFound()
        return material
