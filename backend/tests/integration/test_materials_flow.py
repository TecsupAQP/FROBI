"""M3 on the real stack, with real PDFs parsed by pypdf."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.modules.materials.domain import PdfUnreadable
from frobi.modules.materials.infrastructure import PypdfTextExtractor
from frobi.shared.infrastructure import Settings
from pdf import make_pdf

pytestmark = pytest.mark.integration

SAMPLE_ID = "00000000-0000-4000-8000-00000000a001"


@pytest.fixture
async def live_client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def _enter(client: AsyncClient, alias: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions", json={"alias": alias, "career": "Mecatrónica", "role": "learner"}
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def test_pypdf_reads_the_text_of_a_real_pdf() -> None:
    content = await PypdfTextExtractor().extract(
        make_pdf("Sensores inductivos", "Detectan metales")
    )
    text = "\n".join(content.pages)

    assert "Sensores inductivos" in text
    assert "Detectan metales" in text


async def test_pypdf_rejects_garbage() -> None:
    with pytest.raises(PdfUnreadable):
        await PypdfTextExtractor().extract(b"%PDF-1.4 this is not really a pdf")


async def test_the_sensor_guide_is_listed_and_readable(live_client: AsyncClient) -> None:
    auth = await _enter(live_client, "Ana")

    samples = await live_client.get("/api/v1/materials/samples", headers=auth)
    guide = await live_client.get(f"/api/v1/materials/{SAMPLE_ID}", headers=auth)

    assert [s["id"] for s in samples.json()] == [SAMPLE_ID]
    assert samples.json()[0]["title"] == "Guía de sensores industriales"
    assert guide.status_code == 200
    assert "Sensores inductivos" in guide.json()["extracted_text"]


async def test_pasted_material_is_private(live_client: AsyncClient) -> None:
    ana = await _enter(live_client, "Ana")
    luis = await _enter(live_client, "Luis")

    created = await live_client.post(
        "/api/v1/materials",
        headers=ana,
        json={"title": "Mis apuntes", "kind": "guide", "text": "Un termopar mide temperatura."},
    )
    material_id = created.json()["id"]
    mine = await live_client.get(f"/api/v1/materials/{material_id}", headers=ana)
    theirs = await live_client.get(f"/api/v1/materials/{material_id}", headers=luis)

    assert created.status_code == 201
    assert created.json()["source"] == "paste"
    assert mine.json()["extracted_text"] == "Un termopar mide temperatura."
    assert theirs.status_code == 404
    assert theirs.json()["code"] == "Resource.NotFound"


async def test_upload_a_real_pdf(live_client: AsyncClient) -> None:
    auth = await _enter(live_client, "Ana")

    response = await live_client.post(
        "/api/v1/materials/upload",
        headers=auth,
        data={"title": "Apunte PDF", "kind": "guide"},
        files={
            "file": (
                "apunte.pdf",
                make_pdf("Un sensor capacitivo detecta liquidos"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["source"] == "upload"
    assert "capacitivo detecta liquidos" in response.json()["extracted_text"]


@pytest.mark.parametrize(
    "content",
    [b"no soy un pdf", make_pdf()],
    ids=["not-a-pdf", "pdf-without-text"],
)
async def test_unreadable_pdf_is_422(live_client: AsyncClient, content: bytes) -> None:
    auth = await _enter(live_client, "Ana")

    response = await live_client.post(
        "/api/v1/materials/upload",
        headers=auth,
        data={"title": "Malo"},
        files={"file": ("malo.pdf", content, "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "Materials.PdfUnreadable"


async def test_pdf_over_10_mb_is_422(live_client: AsyncClient) -> None:
    auth = await _enter(live_client, "Ana")

    response = await live_client.post(
        "/api/v1/materials/upload",
        headers=auth,
        data={"title": "Enorme"},
        files={"file": ("enorme.pdf", b"%PDF" + b"0" * (10 * 1024 * 1024), "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "Materials.FileTooLarge"


async def test_work_organizes_my_brief_and_draft(live_client: AsyncClient) -> None:
    auth = await _enter(live_client, "Ana")
    brief = await live_client.post(
        "/api/v1/materials",
        headers=auth,
        json={
            "title": "Consigna",
            "kind": "brief",
            "text": "1. Comparar sensores inductivos y capacitivos.\n2. Dar un ejemplo industrial.",
        },
    )
    draft = await live_client.post(
        "/api/v1/materials",
        headers=auth,
        json={
            "title": "Borrador",
            "kind": "draft",
            "text": "# Comparación\nLos inductivos y capacitivos detectan cosas distintas.",
        },
    )

    work = await live_client.post(
        "/api/v1/works",
        headers=auth,
        json={"brief_material_id": brief.json()["id"], "draft_material_id": draft.json()["id"]},
    )

    assert work.status_code == 201, work.text
    assert work.json()["organized"] == {
        "requirements": ["Comparar sensores inductivos y capacitivos", "Dar un ejemplo industrial"],
        "topics": ["Comparación"],
        "missing": ["Dar un ejemplo industrial"],
    }


async def test_work_with_the_wrong_kinds_is_422(live_client: AsyncClient) -> None:
    auth = await _enter(live_client, "Ana")

    work = await live_client.post(
        "/api/v1/works",
        headers=auth,
        json={"brief_material_id": SAMPLE_ID, "draft_material_id": SAMPLE_ID},
    )

    assert work.status_code == 422
    assert work.json()["code"] == "Materials.WrongKind"


async def test_my_guides_lists_my_own_first_then_the_samples(live_client: AsyncClient) -> None:
    ana = await _enter(live_client, "Ana")
    luis = await _enter(live_client, "Luis")
    for title in ("Motores", "Neumática"):
        await live_client.post(
            "/api/v1/materials",
            headers=ana,
            json={"title": title, "kind": "guide", "text": f"Apuntes de {title}."},
        )
    await live_client.post(
        "/api/v1/materials",
        headers=ana,
        json={"title": "Borrador", "kind": "draft", "text": "Esto no es una guía."},
    )

    mine = await live_client.get("/api/v1/materials/guides", headers=ana)
    theirs = await live_client.get("/api/v1/materials/guides", headers=luis)

    assert mine.status_code == 200
    assert [g["title"] for g in mine.json()] == [
        "Neumática",
        "Motores",
        "Guía de sensores industriales",
    ]
    assert [g["id"] for g in theirs.json()] == [SAMPLE_ID]
