"""Bring your own material: paste text or upload a PDF of up to 10 MB (RF02, RF31)."""

import logging
from dataclasses import replace

from frobi.modules.materials.application.ports import (
    FileStorage,
    FileStorageUnavailable,
    MaterialRepository,
    PdfTextExtractor,
)
from frobi.modules.materials.application.topic_finder import TopicFinder
from frobi.modules.materials.domain import (
    MAX_UPLOAD_BYTES,
    EmptyText,
    FileTooLarge,
    Material,
    MaterialSource,
    PdfUnreadable,
    assemble_pages,
    normalize_text,
    normalize_title,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

from .command import CreateMaterialCommand, UploadMaterialCommand

logger = logging.getLogger(__name__)


class CreateMaterialHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        materials: MaterialRepository,
        clock: Clock,
        topics: TopicFinder | None = None,
    ) -> None:
        self._uow = uow
        self._materials = materials
        self._clock = clock
        self._topics = topics or TopicFinder()

    async def handle(self, command: CreateMaterialCommand) -> Material:
        text = normalize_text(command.text)
        material = Material.create(
            owner_id=command.owner_id,
            title=command.title,
            kind=command.kind,
            source=MaterialSource.PASTE,
            text=text,
            now=self._clock.now(),
            class_id=command.class_id,
            topic_spans=await self._topics.find(normalize_title(command.title), text),
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
        storage: FileStorage | None = None,
        topics: TopicFinder | None = None,
    ) -> None:
        """Without ``storage`` only the extracted text is kept (no preview of the original)."""
        self._uow = uow
        self._materials = materials
        self._extractor = extractor
        self._clock = clock
        self._storage = storage
        self._topics = topics or TopicFinder()

    async def handle(self, command: UploadMaterialCommand) -> Material:
        if len(command.data) > MAX_UPLOAD_BYTES:
            raise FileTooLarge()
        pdf = await self._extractor.extract(command.data)
        text, page_offsets = assemble_pages(list(pdf.pages))
        if not text:
            # A scanned PDF without a text layer reads as empty: tell the person it is unreadable.
            raise PdfUnreadable()
        spans = await self._topics.find(
            normalize_title(command.title),
            text,
            page_offsets=page_offsets,
            outline=pdf.outline,
            headings=pdf.headings,
        )
        try:
            material = Material.create(
                owner_id=command.owner_id,
                title=command.title,
                kind=command.kind,
                source=MaterialSource.UPLOAD,
                text=text,
                now=self._clock.now(),
                class_id=command.class_id,
                topic_spans=spans,
            )
        except EmptyText as error:
            raise PdfUnreadable() from error
        material = await self._store_original(material, command.data)
        try:
            async with self._uow:
                await self._materials.add(material)
                await self._uow.commit()
        except Exception:
            await self._forget_original(material)
            raise
        return material

    async def _store_original(self, material: Material, data: bytes) -> Material:
        """The PDF goes to storage for the preview; if storage fails the text still counts."""
        if self._storage is None:
            return material
        key = material.file_key_for_upload()
        try:
            await self._storage.put(key, data, "application/pdf")
        except FileStorageUnavailable:
            logger.warning("Original PDF of material %s not stored", material.id, exc_info=True)
            return material
        return replace(material, file_key=key)

    async def _forget_original(self, material: Material) -> None:
        if self._storage is None or material.file_key is None:
            return
        try:
            await self._storage.delete(material.file_key)
        except FileStorageUnavailable:
            logger.warning("Orphan PDF left at %s", material.file_key, exc_info=True)
