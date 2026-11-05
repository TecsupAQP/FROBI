"""A material and its text, for whoever may see it. Also part of the public API (adaptations)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.materials.application.ports import FileStorage, MaterialRepository, SampleCatalog
from frobi.modules.materials.domain import Material, MaterialFileNotFound, MaterialNotFound
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


@dataclass(frozen=True, slots=True)
class MaterialFile:
    url: str
    expires_in: int


class GetMaterialFileHandler:
    """A temporary link to the original PDF, for whoever may see the material."""

    def __init__(
        self, materials: GetMaterialHandler, storage: FileStorage | None, expires_in: int
    ) -> None:
        self._materials = materials
        self._storage = storage
        self._expires_in = expires_in

    async def handle(self, person_id: UUID, material_id: UUID) -> MaterialFile:
        material = await self._materials.handle(person_id, material_id)
        if material.file_key is None or self._storage is None:
            raise MaterialFileNotFound()
        url = self._storage.signed_url(
            material.file_key, expires_in=self._expires_in, filename=f"{material.title}.pdf"
        )
        return MaterialFile(url=url, expires_in=self._expires_in)
