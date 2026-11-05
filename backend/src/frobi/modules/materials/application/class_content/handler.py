"""Content a teacher uploads for a class (RF45). Part of the public API, used by classrooms.

Classrooms decides who may upload and read; this only stores and lists ``class_content``.
"""

from uuid import UUID

from frobi.modules.materials.application.create_material import (
    CreateMaterialCommand,
    CreateMaterialHandler,
    UploadMaterialCommand,
    UploadMaterialHandler,
)
from frobi.modules.materials.application.ports import MaterialRepository
from frobi.modules.materials.domain import Material, MaterialKind


class ClassContentHandler:
    def __init__(
        self,
        create: CreateMaterialHandler,
        upload: UploadMaterialHandler,
        materials: MaterialRepository,
    ) -> None:
        self._create = create
        self._upload = upload
        self._materials = materials

    async def add_text(self, owner_id: UUID, class_id: UUID, title: str, text: str) -> Material:
        return await self._create.handle(
            CreateMaterialCommand(
                owner_id=owner_id,
                title=title,
                kind=MaterialKind.CLASS_CONTENT,
                text=text,
                class_id=class_id,
            )
        )

    async def add_pdf(self, owner_id: UUID, class_id: UUID, title: str, data: bytes) -> Material:
        return await self._upload.handle(
            UploadMaterialCommand(
                owner_id=owner_id,
                title=title,
                kind=MaterialKind.CLASS_CONTENT,
                data=data,
                class_id=class_id,
            )
        )

    async def list_for_class(self, class_id: UUID) -> list[Material]:
        return await self._materials.list_for_class(class_id)
