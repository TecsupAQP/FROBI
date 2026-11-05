from uuid import UUID, uuid4

import pytest

from fakes.identity import FakeUnitOfWork, FixedClock
from fakes.materials import (
    SAMPLE,
    FakeExtractor,
    InMemoryMaterials,
    InMemoryWorks,
    StaticSamples,
)
from frobi.modules.materials.application import (
    CreateMaterialCommand,
    CreateMaterialHandler,
    CreateWorkCommand,
    CreateWorkHandler,
    GetMaterialHandler,
    UploadMaterialCommand,
    UploadMaterialHandler,
)
from frobi.modules.materials.domain import (
    MAX_UPLOAD_BYTES,
    FileTooLarge,
    Material,
    MaterialKind,
    MaterialNotFound,
    MaterialSource,
    PdfUnreadable,
    WrongKind,
)

ANA = uuid4()
LUIS = uuid4()


@pytest.fixture
def materials() -> InMemoryMaterials:
    return InMemoryMaterials()


def _get(materials: InMemoryMaterials) -> GetMaterialHandler:
    return GetMaterialHandler(materials, StaticSamples())


async def _paste(
    materials: InMemoryMaterials, kind: MaterialKind, text: str, owner: UUID = ANA
) -> Material:
    return await CreateMaterialHandler(FakeUnitOfWork(), materials, FixedClock()).handle(
        CreateMaterialCommand(owner_id=owner, title=kind.value, kind=kind, text=text)
    )


async def test_pasted_material_is_stored_for_its_owner(materials: InMemoryMaterials) -> None:
    material = await _paste(materials, MaterialKind.GUIDE, "Texto de la guía")

    assert material.source is MaterialSource.PASTE
    assert await _get(materials).handle(ANA, material.id) == material


async def test_someone_elses_material_looks_like_it_does_not_exist(
    materials: InMemoryMaterials,
) -> None:
    material = await _paste(materials, MaterialKind.GUIDE, "Privado")

    with pytest.raises(MaterialNotFound):
        await _get(materials).handle(LUIS, material.id)


async def test_samples_can_be_read_by_anyone(materials: InMemoryMaterials) -> None:
    assert await _get(materials).handle(LUIS, SAMPLE.id) == SAMPLE


async def test_upload_stores_the_extracted_text(materials: InMemoryMaterials) -> None:
    handler = UploadMaterialHandler(FakeUnitOfWork(), materials, FakeExtractor(), FixedClock())

    material = await handler.handle(
        UploadMaterialCommand(
            owner_id=ANA, title="PDF", kind=MaterialKind.GUIDE, data=b"Texto del PDF"
        )
    )

    assert material.source is MaterialSource.UPLOAD
    assert material.text == "Texto del PDF"
    assert materials.items[material.id] == material


@pytest.mark.parametrize("data", [b"%BROKEN", b"   \n  "])
async def test_unreadable_or_textless_pdf_is_rejected_and_not_stored(
    materials: InMemoryMaterials, data: bytes
) -> None:
    handler = UploadMaterialHandler(FakeUnitOfWork(), materials, FakeExtractor(), FixedClock())

    with pytest.raises(PdfUnreadable):
        await handler.handle(
            UploadMaterialCommand(owner_id=ANA, title="PDF", kind=MaterialKind.GUIDE, data=data)
        )
    assert materials.items == {}


async def test_upload_over_10_mb_is_rejected(materials: InMemoryMaterials) -> None:
    handler = UploadMaterialHandler(FakeUnitOfWork(), materials, FakeExtractor(), FixedClock())

    with pytest.raises(FileTooLarge):
        await handler.handle(
            UploadMaterialCommand(
                owner_id=ANA,
                title="PDF",
                kind=MaterialKind.GUIDE,
                data=b"x" * (MAX_UPLOAD_BYTES + 1),
            )
        )


def _work_handler(materials: InMemoryMaterials, works: InMemoryWorks) -> CreateWorkHandler:
    return CreateWorkHandler(FakeUnitOfWork(), _get(materials), works, FixedClock())


async def test_work_organizes_brief_and_draft(materials: InMemoryMaterials) -> None:
    works = InMemoryWorks()
    brief = await _paste(materials, MaterialKind.BRIEF, "- Comparar inductivos y capacitivos")
    draft = await _paste(materials, MaterialKind.DRAFT, "Los inductivos y capacitivos difieren.")

    work = await _work_handler(materials, works).handle(
        CreateWorkCommand(person_id=ANA, brief_material_id=brief.id, draft_material_id=draft.id)
    )

    assert works.items == [work]
    assert work.organized.requirements == ("Comparar inductivos y capacitivos",)
    assert work.organized.missing == ()


async def test_work_needs_a_brief_and_a_draft(materials: InMemoryMaterials) -> None:
    guide = await _paste(materials, MaterialKind.GUIDE, "Guía")
    draft = await _paste(materials, MaterialKind.DRAFT, "Borrador")

    with pytest.raises(WrongKind):
        await _work_handler(materials, InMemoryWorks()).handle(
            CreateWorkCommand(person_id=ANA, brief_material_id=guide.id, draft_material_id=draft.id)
        )


async def test_work_cannot_use_someone_elses_material(materials: InMemoryMaterials) -> None:
    brief = await _paste(materials, MaterialKind.BRIEF, "- Algo importante", owner=LUIS)
    draft = await _paste(materials, MaterialKind.DRAFT, "Borrador")

    with pytest.raises(MaterialNotFound):
        await _work_handler(materials, InMemoryWorks()).handle(
            CreateWorkCommand(person_id=ANA, brief_material_id=brief.id, draft_material_id=draft.id)
        )
