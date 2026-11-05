"""M2 and /me/settings on the real stack: Postgres (frobi_test) and Redis (db 15)."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration


@pytest.fixture
async def live_client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


@pytest.fixture
async def auth(live_client: AsyncClient) -> dict[str, str]:
    response = await live_client.post(
        "/api/v1/sessions", json={"alias": "Rosa", "career": "Química", "role": "learner"}
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def test_new_person_has_default_settings_and_pending_wizard(
    live_client: AsyncClient, auth: dict[str, str]
) -> None:
    me = await live_client.get("/api/v1/me", headers=auth)
    settings = await live_client.get("/api/v1/me/settings", headers=auth)

    assert me.json()["onboarding"] == {"done": False, "intro_status": "pending"}
    assert settings.status_code == 200
    assert settings.json()["language"] == "es"
    assert not any(settings.json()[name] for name in ("voice", "large_text", "captions"))


async def test_completing_the_wizard_is_reflected_in_me_and_settings(
    live_client: AsyncClient, auth: dict[str, str]
) -> None:
    done = await live_client.post(
        "/api/v1/me/onboarding",
        headers=auth,
        json={"who_uses": "companion", "profiles": ["low_vision", "motor"], "intro": "seen"},
    )
    me = await live_client.get("/api/v1/me", headers=auth)
    settings = (await live_client.get("/api/v1/me/settings", headers=auth)).json()

    assert done.status_code == 200, done.text
    assert done.json()["enabled_settings"] == [
        "voice",
        "high_contrast",
        "large_text",
        "large_buttons",
        "keyboard_mode",
    ]
    assert me.json()["onboarding"] == {"done": True, "intro_status": "seen"}
    assert me.json()["person"]["configured_by"] == "companion"
    assert settings["profiles"] == ["low_vision", "motor"]
    assert settings["voice"] is True
    assert settings["captions"] is False


async def test_patch_settings_changes_only_what_is_sent(
    live_client: AsyncClient, auth: dict[str, str]
) -> None:
    await live_client.patch("/api/v1/me/settings", headers=auth, json={"voice": True})

    response = await live_client.patch("/api/v1/me/settings", headers=auth, json={"captions": True})

    assert response.status_code == 200
    assert response.json()["voice"] is True
    assert response.json()["captions"] is True


async def test_quechua_is_not_available_yet(live_client: AsyncClient, auth: dict[str, str]) -> None:
    response = await live_client.patch("/api/v1/me/settings", headers=auth, json={"language": "qu"})

    assert response.status_code == 422
    assert response.json()["code"] == "Settings.LanguageNotAvailable"


async def test_skip_then_reset(live_client: AsyncClient, auth: dict[str, str]) -> None:
    skipped = await live_client.post("/api/v1/me/onboarding/skip", headers=auth)
    after_skip = (await live_client.get("/api/v1/me", headers=auth)).json()["onboarding"]
    reset = await live_client.post("/api/v1/me/onboarding/reset", headers=auth)
    after_reset = (await live_client.get("/api/v1/me", headers=auth)).json()["onboarding"]

    assert skipped.json()["intro_status"] == "skipped"
    assert after_skip == {"done": True, "intro_status": "skipped"}
    assert reset.json()["done"] is False
    assert after_reset == {"done": False, "intro_status": "pending"}
