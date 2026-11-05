"""A long PDF on the real stack: split into topics, and each format reads only its topic."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.shared.infrastructure import Settings
from pdf import make_structured_pdf

pytestmark = pytest.mark.integration

INDUCTIVE = [
    "El sensor inductivo detecta metales sin contacto fisico en la linea de produccion.",
    "Su bobina genera un campo magnetico que cambia cuando se acerca una pieza metalica.",
    "La distancia de deteccion depende del tamano de la bobina y del tipo de metal.",
    "Se usa para contar piezas de acero en una faja transportadora sin desgaste.",
]
CAPACITIVE = [
    "El sensor capacitivo detecta liquidos y plasticos a traves de un envase de vidrio.",
    "Mide el cambio de capacitancia entre su placa y el objeto que tiene delante.",
    "Un tornillo de ajuste regula la sensibilidad para ignorar la pared del tanque.",
    "Se instala en tolvas para avisar cuando el nivel de granos llega al limite.",
]


@pytest.fixture
async def client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def _enter(client: AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions", json={"alias": "Ana", "career": "Mecatrónica", "role": "learner"}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


def _long_pdf() -> bytes:
    inductive = [(line, 11) for line in INDUCTIVE * 2]
    capacitive = [(line, 11) for line in CAPACITIVE * 2]
    return make_structured_pdf(
        [inductive, inductive, capacitive, capacitive],
        outline=[("Sensores inductivos", 0), ("Sensores capacitivos", 2)],
    )


async def _upload(client: AsyncClient, auth: dict[str, str]) -> dict[str, object]:
    response = await client.post(
        "/api/v1/materials/upload",
        headers=auth,
        data={"title": "Sensores", "kind": "guide"},
        files={"file": ("sensores.pdf", _long_pdf(), "application/pdf")},
    )
    assert response.status_code == 201, response.text
    return dict(response.json())


async def test_an_uploaded_pdf_comes_split_into_topics_with_pages(client: AsyncClient) -> None:
    material = await _upload(client, await _enter(client))

    topics = material["topics"]
    assert [(t["position"], t["title"], t["page_start"], t["page_end"]) for t in topics] == [  # type: ignore[union-attr, index]
        (1, "Sensores inductivos", 1, 2),
        (2, "Sensores capacitivos", 3, 4),
    ]


async def test_each_format_hint_and_question_reads_only_its_topic(client: AsyncClient) -> None:
    auth = await _enter(client)
    material = await _upload(client, auth)

    adaptation = await client.post(
        f"/api/v1/materials/{material['id']}/adaptations",
        headers=auth,
        json={"format": "easy_read", "topic": 2},
    )

    assert adaptation.status_code == 201, adaptation.text
    body = adaptation.json()
    assert body["topic"] == 2
    assert body["content"]["title"] == "Sensores · Sensores capacitivos"
    assert "capacitivo" in body["content"]["plain_text"]
    assert "inductivo" not in body["content"]["plain_text"]
    questions = await client.post(f"/api/v1/adaptations/{body['id']}/questions", headers=auth)
    assert questions.status_code in (200, 201), questions.text
    statements = " ".join(str(q) for q in questions.json())
    assert "inductivo" not in statements


async def test_a_topic_that_does_not_exist_is_not_found(client: AsyncClient) -> None:
    auth = await _enter(client)
    material = await _upload(client, auth)

    response = await client.post(
        f"/api/v1/materials/{material['id']}/adaptations",
        headers=auth,
        json={"format": "easy_read", "topic": 9},
    )

    assert response.status_code == 404
