"""The Claude tool loop against a scripted SDK client (no network)."""

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest
from anthropic.types.beta import BetaMessage

from fakes.assistant import LEARNER
from frobi.modules.assistant.application.ports import (
    Answered,
    AssistantTool,
    AssistantUnavailable,
    JsonObject,
    TextChunk,
    ToolFailed,
    ToolUsed,
)
from frobi.modules.assistant.infrastructure import ClaudeAssistant


def _message(stop_reason: str, content: list[dict[str, Any]]) -> BetaMessage:
    return BetaMessage.model_validate(
        {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "model": "claude-opus-5-5",
            "content": content,
            "stop_reason": stop_reason,
            "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }
    )


@dataclass
class _Stream:
    message: BetaMessage

    async def __aenter__(self) -> "_Stream":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    def __aiter__(self) -> AsyncIterator[Any]:
        return self._events()

    async def _events(self) -> AsyncIterator[Any]:
        for block in self.message.content:
            if block.type == "text":
                yield SimpleNamespace(type="text", text=block.text)

    async def get_final_message(self) -> BetaMessage:
        return self.message


class ScriptedClient:
    def __init__(self, *replies: BetaMessage | Exception) -> None:
        self.replies = list(replies)
        self.requests: list[dict[str, Any]] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **kwargs: Any) -> _Stream:
        # Snapshot: the loop keeps appending to the same list.
        self.requests.append({**kwargs, "messages": json.loads(json.dumps(kwargs["messages"]))})
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return _Stream(reply)


def _tool(seen: list[JsonObject]) -> AssistantTool:
    async def run(arguments: JsonObject) -> JsonObject:
        seen.append(arguments)
        if arguments.get("fail"):
            raise ToolFailed("No existe.")
        return {"solved_without_ai": 2}

    return AssistantTool("my_progress", "Progress.", {"type": "object"}, "Revisando…", run)


async def _collect(assistant: ClaudeAssistant, tools: list[AssistantTool]) -> list[Any]:
    return [
        event
        async for event in assistant.reply(
            person=LEARNER,
            history=[
                {"role": "user", "content": "Hola"},
                {"role": "assistant", "content": "¡Hola!"},
            ],
            question="¿Cómo voy?",
            tools=tools,
        )
    ]


async def test_runs_a_tool_and_answers() -> None:
    seen: list[JsonObject] = []
    client = ScriptedClient(
        _message(
            "tool_use",
            [{"type": "tool_use", "id": "toolu_1", "name": "my_progress", "input": {}}],
        ),
        _message("end_turn", [{"type": "text", "text": "Resolviste 2 tareas sin IA."}]),
    )
    assistant = ClaudeAssistant(api_key="k", client=client)  # type: ignore[arg-type]

    events = await _collect(assistant, [_tool(seen)])

    assert events[0] == ToolUsed("Revisando…")
    assert events[1] == TextChunk("Resolviste 2 tareas sin IA.")
    assert isinstance(events[-1], Answered)
    assert seen == [{}]
    first, second = client.requests
    assert first["model"] == "claude-opus-5-5"
    assert first["fallbacks"] == "default"
    assert first["betas"] == ["server-side-fallback-2026-07-01"]
    assert first["output_config"] == {"effort": "medium"}
    assert first["cache_control"] == {"type": "ephemeral"}
    assert first["tools"][0]["eager_input_streaming"] is True
    assert "Ana" in first["system"][1]["text"]
    # The history goes back unchanged, then the tool result in one user message.
    assert second["messages"][:3] == first["messages"]
    result = second["messages"][-1]["content"][0]
    assert result["tool_use_id"] == "toolu_1"
    assert json.loads(result["content"]) == {"solved_without_ai": 2}
    state = events[-1].model_state
    assert state[-1]["content"][0]["text"] == "Resolviste 2 tareas sin IA."


async def test_tool_errors_go_back_to_the_model() -> None:
    client = ScriptedClient(
        _message(
            "tool_use",
            [{"type": "tool_use", "id": "t", "name": "my_progress", "input": {"fail": "1"}}],
        ),
        _message("end_turn", [{"type": "text", "text": "No encontré eso."}]),
    )

    await _collect(ClaudeAssistant(api_key="k", client=client), [_tool([])])  # type: ignore[arg-type]

    result = client.requests[1]["messages"][-1]["content"][0]
    assert result == {
        "type": "tool_result",
        "tool_use_id": "t",
        "is_error": True,
        "content": "No existe.",
    }


async def test_malformed_tool_input_is_not_run() -> None:
    seen: list[JsonObject] = []
    client = ScriptedClient(
        _message(
            "tool_use",
            [{"type": "tool_use", "id": "t", "name": "my_progress", "input": {"x": {"y": 1}}}],
        ),
        _message("end_turn", [{"type": "text", "text": "Listo."}]),
    )

    await _collect(ClaudeAssistant(api_key="k", client=client), [_tool(seen)])  # type: ignore[arg-type]

    assert seen == []
    assert client.requests[1]["messages"][-1]["content"][0]["is_error"] is True


async def test_refusal_and_api_errors_become_unavailable() -> None:
    refused = ScriptedClient(_message("refusal", []))
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    failing = ScriptedClient(anthropic.APIConnectionError(request=request))

    for client in (refused, failing):
        with pytest.raises(AssistantUnavailable):
            await _collect(ClaudeAssistant(api_key="k", client=client), [])  # type: ignore[arg-type]
