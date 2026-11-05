"""Bring your own material: paste text or upload a PDF of up to 10 MB (RF02, RF31)."""

from frobi.modules.materials.application.ports import MaterialRepository, PdfTextExtractor
from frobi.modules.materials.domain import (
    MAX_UPLOAD_BYTES,
    EmptyText,
    FileTooLarge,
    Material,
    MaterialSource,
    PdfUnreadable,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

from .command import CreateMaterialCommand, UploadMaterialCommand


class CreateMaterialHandler:
    def __init__(self, uow: UnitOfWork, materials: MaterialRepository, clock: Clock) -> None:
        self._uow = uow
        self._materials = materials
        self._clock = clock

    async def handle(self, command: CreateMaterialCommand) -> Material:
        material = Material.create(
            owner_id=command.owner_id,
            title=command.title,
            kind=command.kind,
            source=MaterialSource.PASTE,
            text=command.text,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._materials.add(material)
            await self._uow.commit()
        return material


class UploadMaterialHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        materials: MaterialRepository,
        extractor: PdfTextExtractor,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._materials = materials
        self._extractor = extractor
        self._clock = clock

    async def handle(self, command: UploadMaterialCommand) -> Material:
        if len(command.data) > MAX_UPLOAD_BYTES:
            raise FileTooLarge()
        text = await self._extractor.extract(command.data)
        try:
            material = Material.create(
                owner_id=command.owner_id,
                title=command.title,
                kind=command.kind,
                source=MaterialSource.UPLOAD,
                text=text,
                now=self._clock.now(),
            )
        except EmptyText as error:
            # A scanned PDF without a text layer reads as empty: tell the person it is unreadable.
            raise PdfUnreadable() from error
        async with self._uow:
            await self._materials.add(material)
            await self._uow.commit()
        return material
