"""The original PDF goes to file storage so the guide can show it (preview)."""

from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4

import httpx
import pytest

from fakes.identity import FakeUnitOfWork, FixedClock
from fakes.materials import (
    SAMPLE,
    FakeExtractor,
    InMemoryFileStorage,
    InMemoryMaterials,
    StaticSamples,
)
from frobi.modules.materials.application import (
    CreateMaterialCommand,
    CreateMaterialHandler,
    GetMaterialFileHandler,
    GetMaterialHandler,
    UploadMaterialCommand,
    UploadMaterialHandler,
)
from frobi.modules.materials.domain import MaterialFileNotFound, MaterialKind, MaterialNotFound
from frobi.modules.materials.infrastructure import R2FileStorage

ANA = uuid4()
LUIS = uuid4()


def _upload(materials: InMemoryMaterials, storage: InMemoryFileStorage) -> UploadMaterialHandler:
    return UploadMaterialHandler(
        FakeUnitOfWork(), materials, FakeExtractor(), FixedClock(), storage
    )


def _file(materials: InMemoryMaterials, storage: InMemoryFileStorage) -> GetMaterialFileHandler:
    return GetMaterialFileHandler(GetMaterialHandler(materials, StaticSamples()), storage, 900)


def _command(owner: UUID = ANA) -> UploadMaterialCommand:
    return UploadMaterialCommand(
        owner_id=owner,
        title="Apunte",
        kind=MaterialKind.GUIDE,
        data=b"Texto del PDF",
    )


async def test_upload_keeps_the_original_pdf_in_storage() -> None:
    materials, storage = InMemoryMaterials(), InMemoryFileStorage()

    material = await _upload(materials, storage).handle(_command())

    assert material.file_key == f"materials/{ANA}/{material.id}.pdf"
    assert storage.files[material.file_key] == b"Texto del PDF"
    assert materials.items[material.id].has_file


async def test_upload_still_works_when_storage_is_down() -> None:
    materials = InMemoryMaterials()

    material = await _upload(materials, InMemoryFileStorage(broken=True)).handle(_command())

    assert material.file_key is None
    assert materials.items[material.id].text == "Texto del PDF"


async def test_owner_gets_a_temporary_link_to_the_original() -> None:
    materials, storage = InMemoryMaterials(), InMemoryFileStorage()
    material = await _upload(materials, storage).handle(_command())

    file = await _file(materials, storage).handle(ANA, material.id)

    assert file.url.startswith(f"https://files.test/{material.file_key}")
    assert file.expires_in == 900


async def test_nobody_else_gets_the_link() -> None:
    materials, storage = InMemoryMaterials(), InMemoryFileStorage()
    material = await _upload(materials, storage).handle(_command())

    with pytest.raises(MaterialNotFound):
        await _file(materials, storage).handle(LUIS, material.id)


async def test_pasted_text_and_samples_have_no_original() -> None:
    materials, storage = InMemoryMaterials(), InMemoryFileStorage()
    pasted = await CreateMaterialHandler(FakeUnitOfWork(), materials, FixedClock()).handle(
        CreateMaterialCommand(owner_id=ANA, title="T", kind=MaterialKind.GUIDE, text="Texto")
    )

    for material_id in (pasted.id, SAMPLE.id):
        with pytest.raises(MaterialFileNotFound):
            await _file(materials, storage).handle(ANA, material_id)


def _r2(handler: httpx.MockTransport | None = None) -> R2FileStorage:
    return R2FileStorage(
        endpoint="https://account.r2.cloudflarestorage.com",
        access_key_id="AKID",
        secret_access_key="secret",
        bucket="frobi",
        transport=handler,
    )


def test_signed_url_is_private_inline_and_expires() -> None:
    url = urlsplit(_r2().signed_url("materials/a/b.pdf", expires_in=900, filename="Guía.pdf"))
    query = parse_qs(url.query)

    assert url.netloc == "account.r2.cloudflarestorage.com"
    assert url.path == "/frobi/materials/a/b.pdf"
    assert query["X-Amz-Expires"] == ["900"]
    assert query["X-Amz-Credential"][0].startswith("AKID/")
    assert query["response-content-type"] == ["application/pdf"]
    assert query["response-content-disposition"][0].startswith("inline;")
    assert len(query["X-Amz-Signature"][0]) == 64


async def test_put_sends_a_signed_request() -> None:
    seen: list[httpx.Request] = []

    def answer(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200)

    await _r2(httpx.MockTransport(answer)).put("materials/a/b.pdf", b"%PDF", "application/pdf")

    [request] = seen
    assert request.method == "PUT"
    assert request.url.path == "/frobi/materials/a/b.pdf"
    assert request.headers["authorization"].startswith("AWS4-HMAC-SHA256 Credential=AKID/")
    assert request.content == b"%PDF"
