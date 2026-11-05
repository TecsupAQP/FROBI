"""Content of the class (RF45): the teacher uploads it, the teacher and joined students read it."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.classrooms.application.manage_class import GetClassHandler, own_class
from frobi.modules.classrooms.application.ports import (
    ClassMaterial,
    ClassMaterials,
    ClassRepository,
)
from frobi.modules.classrooms.domain import MissingClassContent


@dataclass(frozen=True, slots=True)
class UploadClassContentCommand:
    teacher_id: UUID
    class_id: UUID
    title: str
    text: str | None = None
    pdf: bytes | None = None


class UploadClassContentHandler:
    def __init__(self, classes: ClassRepository, materials: ClassMaterials) -> None:
        self._classes = classes
        self._materials = materials

    async def handle(self, command: UploadClassContentCommand) -> ClassMaterial:
        await own_class(self._classes, command.teacher_id, command.class_id)
        has_text = command.text is not None and command.text.strip() != ""
        has_pdf = command.pdf is not None
        if has_text == has_pdf:
            raise MissingClassContent()
        if command.pdf is not None:
            return await self._materials.add_pdf(
                command.teacher_id, command.class_id, command.title, command.pdf
            )
        assert command.text is not None
        return await self._materials.add_text(
            command.teacher_id, command.class_id, command.title, command.text
        )


class ListClassContentHandler:
    """Same rule as seeing the class: its teacher, or a student joined to it right now."""

    def __init__(self, get_class: GetClassHandler, materials: ClassMaterials) -> None:
        self._get_class = get_class
        self._materials = materials

    async def handle(self, person_id: UUID, class_id: UUID) -> list[ClassMaterial]:
        await self._get_class.handle(person_id, class_id)
        return await self._materials.list_for_class(class_id)
