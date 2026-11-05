from uuid import UUID, uuid4

import pytest

from fakes.identity import FakeUnitOfWork, FixedClock
from fakes.materials import (
    SAMPLE,
    FakeExtractor,
    FixedClassContext,
    InMemoryMaterials,
    InMemoryWorks,
    StaticSamples,
)
from frobi.modules.materials.application import (
    ClassContentHandler,
    CreateMaterialCommand,
    CreateMaterialHandler,
    CreateWorkCommand,
    CreateWorkHandler,
    GetMaterialHandler,
    GuidesHandler,
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


CLASS, OTHER_CLASS, PROFE = uuid4(), uuid4(), uuid4()


def _class_content(materials: InMemoryMaterials) -> ClassContentHandler:
    return ClassContentHandler(
        CreateMaterialHandler(FakeUnitOfWork(), materials, FixedClock()),
        UploadMaterialHandler(FakeUnitOfWork(), materials, FakeExtractor(), FixedClock()),
        materials,
    )


async def test_class_content_is_stored_with_its_class(materials: InMemoryMaterials) -> None:
    content = _class_content(materials)

    pasted = await content.add_text(PROFE, CLASS, "Guía de la clase", "Sensores capacitivos")
    pdf = await content.add_pdf(PROFE, CLASS, "PDF de la clase", b"Sensores inductivos")

    assert {m.kind for m in (pasted, pdf)} == {MaterialKind.CLASS_CONTENT}
    assert {m.class_id for m in (pasted, pdf)} == {CLASS}
    assert await content.list_for_class(CLASS) == [pasted, pdf]
    assert await content.list_for_class(OTHER_CLASS) == []


async def test_class_content_is_visible_only_inside_its_class(materials: InMemoryMaterials) -> None:
    material = await _class_content(materials).add_text(PROFE, CLASS, "Guía", "Texto")
    get = GetMaterialHandler(
        materials, StaticSamples(), FixedClassContext({ANA: CLASS, LUIS: OTHER_CLASS})
    )

    assert await get.find(PROFE, material.id) == material
    assert await get.find(ANA, material.id) == material
    assert await get.find(LUIS, material.id) is None
    assert await get.find(uuid4(), material.id) is None


async def test_without_a_class_context_class_content_stays_with_its_teacher(
    materials: InMemoryMaterials,
) -> None:
    material = await _class_content(materials).add_text(PROFE, CLASS, "Guía", "Texto")

    assert await _get(materials).find(ANA, material.id) is None


async def test_a_private_material_never_leaks_into_the_class(materials: InMemoryMaterials) -> None:
    """Only ``class_content`` is shared: a guide of the teacher with a class_id stays private."""
    own = await CreateMaterialHandler(FakeUnitOfWork(), materials, FixedClock()).handle(
        CreateMaterialCommand(PROFE, "Mía", MaterialKind.GUIDE, "Privado", class_id=CLASS)
    )
    get = GetMaterialHandler(materials, StaticSamples(), FixedClassContext({ANA: CLASS}))

    assert await get.find(ANA, own.id) is None


async def test_guides_include_the_content_of_the_active_class(materials: InMemoryMaterials) -> None:
    of_class = await _class_content(materials).add_text(PROFE, CLASS, "Guía", "Texto")
    own = await _paste(materials, MaterialKind.GUIDE, "Mía")
    guides = GuidesHandler(materials, StaticSamples(), FixedClassContext({ANA: CLASS}))

    assert await guides.for_person(ANA) == [own, of_class, SAMPLE]
    assert await guides.for_person(LUIS) == [SAMPLE]
