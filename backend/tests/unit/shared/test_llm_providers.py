"""The real providers, against a fake HTTP transport: no network, no key."""

import json

import httpx
import pytest

from frobi.shared.infrastructure.llm import (
    AnthropicLlmClient,
    DisabledLlmClient,
    LlmUnavailable,
    OpenAiCompatibleLlmClient,
    build_llm_client,
    parse_json_object,
)


def _transport(status: int, body: object, seen: list[httpx.Request]) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status, json=body)

    return httpx.MockTransport(handle)


async def test_anthropic_sends_system_and_prompt_and_parses_the_json() -> None:
    seen: list[httpx.Request] = []
    reply = {"content": [{"type": "text", "text": '```json\n{"text": "Hola"}\n```'}]}
    client = AnthropicLlmClient(api_key="k", model="m", transport=_transport(200, reply, seen))

    result = await client.complete_json(system="Reglas", prompt="Adapta")

    assert result == {"text": "Hola"}
    sent = json.loads(seen[0].content)
    assert str(seen[0].url) == "https://api.anthropic.com/v1/messages"
    assert seen[0].headers["x-api-key"] == "k"
    assert (sent["model"], sent["system"]) == ("m", "Reglas")
    assert sent["messages"] == [{"role": "user", "content": "Adapta"}]


async def test_openai_compatible_uses_its_base_url_and_json_mode() -> None:
    seen: list[httpx.Request] = []
    reply = {"choices": [{"message": {"content": '{"ok": true}'}}]}
    client = OpenAiCompatibleLlmClient(
        api_key="k",
        model="llama",
        base_url="https://api.groq.com/openai/v1/",
        transport=_transport(200, reply, seen),
    )

    result = await client.complete_json(system="Reglas", prompt="Adapta")

    assert result == {"ok": True}
    sent = json.loads(seen[0].content)
    assert str(seen[0].url) == "https://api.groq.com/openai/v1/chat/completions"
    assert seen[0].headers["authorization"] == "Bearer k"
    assert sent["response_format"] == {"type": "json_object"}
    assert sent["messages"][0] == {"role": "system", "content": "Reglas"}


@pytest.mark.parametrize(
    ("status", "body"),
    [
        (429, {"error": "rate limited"}),
        (500, {"error": "boom"}),
        (200, {"content": "not a list"}),
        (200, {"content": [{"type": "text", "text": "Sin JSON"}]}),
        (200, {"content": [{"type": "text", "text": "[1, 2]"}]}),
        # Cut at the token limit: even if it happened to parse, the content is incomplete.
        (200, {"stop_reason": "max_tokens", "content": [{"type": "text", "text": '{"a": 1}'}]}),
    ],
)
async def test_any_provider_problem_is_llm_unavailable(status: int, body: object) -> None:
    client = AnthropicLlmClient(api_key="k", transport=_transport(status, body, []))

    with pytest.raises(LlmUnavailable):
        await client.complete_json(system="s", prompt="p")


async def test_a_network_error_is_llm_unavailable() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    client = AnthropicLlmClient(api_key="k", transport=httpx.MockTransport(fail))

    with pytest.raises(LlmUnavailable):
        await client.complete_json(system="s", prompt="p")


def test_json_inside_a_sentence_is_found() -> None:
    assert parse_json_object('Aquí está: {"a": {"b": 1}} listo.') == {"a": {"b": 1}}


def test_without_a_key_there_is_no_provider() -> None:
    client = build_llm_client(
        provider="anthropic", api_key=None, model=None, base_url=None, timeout_seconds=15
    )

    assert isinstance(client, DisabledLlmClient)


def test_the_provider_comes_from_the_settings() -> None:
    def build(provider: str, model: str | None) -> object:
        return build_llm_client(
            provider=provider, api_key="k", model=model, base_url=None, timeout_seconds=15
        )

    assert isinstance(build("anthropic", None), AnthropicLlmClient)
    assert isinstance(build("openai", "gpt"), OpenAiCompatibleLlmClient)
    with pytest.raises(ValueError, match="FROBI_LLM_MODEL"):
        build("openai", None)
    with pytest.raises(ValueError, match="Unknown"):
        build("other", None)
