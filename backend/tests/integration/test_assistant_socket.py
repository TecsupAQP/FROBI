"""M14 on the real stack: the assistant WebSocket over Postgres, Redis and its pub/sub hub."""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from starlette.websockets import WebSocketDisconnect

from fakes.assistant import ScriptedModel
from frobi.main import create_app
from frobi.modules.assistant.application.fallback import UNAVAILABLE
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

WS = "/api/v1/assistant/ws"


@pytest.fixture
def client(test_settings: Settings, migrated_database: str, redis: "Redis") -> Iterator[TestClient]:
    with TestClient(create_app(test_settings)) as test_client:
        yield test_client


def _token(client: TestClient, alias: str = "Ana") -> str:
    response = client.post(
        "/api/v1/sessions", json={"alias": alias, "career": "Mecatrónica", "role": "learner"}
    )
    assert response.status_code == 201, response.text
    return str(response.json()["token"])


def _until(socket: Any, kind: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    while True:
        events.append(socket.receive_json())
        if events[-1]["type"] == kind:
            return events


def _connect(socket: Any, token: str) -> None:
    socket.send_json({"type": "auth", "token": token})
    assert socket.receive_json() == {"type": "ready"}


def test_without_ai_the_answer_is_the_fallback_and_is_not_kept(client: TestClient) -> None:
    token = _token(client)
    with client.websocket_connect(WS) as socket:
        _connect(socket, token)
        socket.send_json({"type": "ask", "question": "¿Cómo subo una guía?"})

        events = _until(socket, "done")

    assert events[0] == {"type": "question", "text": "¿Cómo subo una guía?"}
    assert {"type": "text", "text": UNAVAILABLE} in events
    assert events[-1] == {"type": "done", "fallback": True, "questions_left": 30}
    conversation = client.get(
        "/api/v1/assistant/conversation", headers={"Authorization": f"Bearer {token}"}
    ).json()
    assert conversation == {"enabled": False, "lines": [], "questions_left": 30, "answering": False}


def test_every_open_tab_of_the_person_sees_the_answer(client: TestClient) -> None:
    client.app.state.assistant = ScriptedModel()  # type: ignore[attr-defined]
    token = _token(client)
    with client.websocket_connect(WS) as first, client.websocket_connect(WS) as second:
        _connect(first, token)
        _connect(second, token)
        first.send_json({"type": "ask", "question": "Hola"})

        seen_by_first = _until(first, "done")
        seen_by_second = _until(second, "done")

    assert seen_by_first == seen_by_second
    assert [e["text"] for e in seen_by_second if e["type"] == "text"] == ["Hola", ", Ana."]
    lines = client.get(
        "/api/v1/assistant/conversation", headers={"Authorization": f"Bearer {token}"}
    ).json()["lines"]
    assert lines == [
        {"speaker": "person", "text": "Hola"},
        {"speaker": "assistant", "text": "Hola, Ana."},
    ]


def test_other_people_do_not_see_it(client: TestClient) -> None:
    client.app.state.assistant = ScriptedModel()  # type: ignore[attr-defined]
    ana, luis = _token(client, "Ana"), _token(client, "Luis")
    with client.websocket_connect(WS) as socket_ana, client.websocket_connect(WS) as socket_luis:
        _connect(socket_ana, ana)
        _connect(socket_luis, luis)
        socket_ana.send_json({"type": "ask", "question": "Hola"})
        _until(socket_ana, "done")

        socket_luis.send_json({"type": "ping"})
        assert socket_luis.receive_json() == {"type": "pong"}


def test_a_rejected_question_only_goes_back_to_the_socket_that_asked(client: TestClient) -> None:
    token = _token(client)
    with client.websocket_connect(WS) as socket:
        _connect(socket, token)
        socket.send_json({"type": "ask", "question": "   "})

        assert socket.receive_json()["code"] == "Assistant.EmptyQuestion"


def test_restart_reaches_the_open_sockets(client: TestClient) -> None:
    client.app.state.assistant = ScriptedModel()  # type: ignore[attr-defined]
    token = _token(client)
    auth = {"Authorization": f"Bearer {token}"}
    with client.websocket_connect(WS) as socket:
        _connect(socket, token)
        socket.send_json({"type": "ask", "question": "Hola"})
        _until(socket, "done")

        assert client.delete("/api/v1/assistant/conversation", headers=auth).status_code == 204
        assert socket.receive_json() == {"type": "restarted"}
    assert client.get("/api/v1/assistant/conversation", headers=auth).json()["lines"] == []


def test_an_invalid_token_closes_the_socket(client: TestClient) -> None:
    with client.websocket_connect(WS) as socket:
        socket.send_json({"type": "auth", "token": "nope"})
        with pytest.raises(WebSocketDisconnect) as closed:
            socket.receive_json()
    assert closed.value.code == 4401
