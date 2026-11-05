"""Real AI providers behind ``LlmClient``. Chosen by ``FROBI_LLM_PROVIDER``; off without a key.

- ``anthropic``: Anthropic Messages API (Claude).
- ``openai``: any OpenAI-compatible Chat Completions API (OpenAI, Groq, OpenRouter, Gemini's
  OpenAI endpoint, a local Ollama…). Set ``FROBI_LLM_BASE_URL`` and ``FROBI_LLM_MODEL``.

Both only ask for a JSON object and parse it; callers validate its shape and fall back on any
error, so a provider failure is never seen by the person (RNF03, RNF06).
"""

import json
from typing import Any

import httpx

from .client import DisabledLlmClient, LlmClient, LlmUnavailable

ANTHROPIC_URL = "https://api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_ANTHROPIC_MODEL = "claude-haiku-5-5"
OPENAI_URL = "https://api.openai.com/v1"
MAX_OUTPUT_TOKENS = 2048


def parse_json_object(text: str) -> dict[str, Any]:
    """The JSON object in a reply, tolerating ```json fences or a sentence around it."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LlmUnavailable("The reply has no JSON object")
    try:
        value = json.loads(text[start : end + 1])
    except json.JSONDecodeError as error:
        raise LlmUnavailable("The reply is not valid JSON") from error
    if not isinstance(value, dict):
        raise LlmUnavailable("The reply is not a JSON object")
    return value


class _HttpLlmClient:
    def __init__(self, *, timeout_seconds: float, transport: httpx.AsyncBaseTransport | None):
        self._timeout = timeout_seconds
        self._transport = transport

    async def _post(self, url: str, headers: dict[str, str], body: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as http:
            try:
                response = await http.post(url, headers=headers, json=body)
            except httpx.HTTPError as error:
                raise LlmUnavailable(f"Provider unreachable: {type(error).__name__}") from error
        if response.status_code != httpx.codes.OK:
            # The body may echo the request; keep only the status in logs.
            raise LlmUnavailable(f"Provider answered {response.status_code}")
        try:
            return response.json()
        except ValueError as error:
            raise LlmUnavailable("Provider answered something that is not JSON") from error


class AnthropicLlmClient(_HttpLlmClient):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_ANTHROPIC_MODEL,
        base_url: str = ANTHROPIC_URL,
        timeout_seconds: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        super().__init__(timeout_seconds=timeout_seconds, transport=transport)
        self._api_key = api_key
        self._model = model
        self._url = base_url.rstrip("/") + "/v1/messages"

    async def complete_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        reply = await self._post(
            self._url,
            {
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
            {
                "model": self._model,
                "max_tokens": MAX_OUTPUT_TOKENS,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        try:
            text = "".join(
                block["text"] for block in reply["content"] if block.get("type") == "text"
            )
        except (KeyError, TypeError, AttributeError) as error:
            raise LlmUnavailable("Unexpected Anthropic reply") from error
        return parse_json_object(text)


class OpenAiCompatibleLlmClient(_HttpLlmClient):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = OPENAI_URL,
        timeout_seconds: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        super().__init__(timeout_seconds=timeout_seconds, transport=transport)
        self._api_key = api_key
        self._model = model
        self._url = base_url.rstrip("/") + "/chat/completions"

    async def complete_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        reply = await self._post(
            self._url,
            {"Authorization": f"Bearer {self._api_key}", "content-type": "application/json"},
            {
                "model": self._model,
                "max_tokens": MAX_OUTPUT_TOKENS,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        try:
            text = reply["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LlmUnavailable("Unexpected OpenAI-compatible reply") from error
        if not isinstance(text, str):
            raise LlmUnavailable("Unexpected OpenAI-compatible reply")
        return parse_json_object(text)


def build_llm_client(
    *,
    provider: str,
    api_key: str | None,
    model: str | None,
    base_url: str | None,
    timeout_seconds: float,
) -> LlmClient:
    """The configured provider, or ``DisabledLlmClient`` when there is no key."""
    if not api_key:
        return DisabledLlmClient()
    if provider == "anthropic":
        return AnthropicLlmClient(
            api_key=api_key,
            model=model or DEFAULT_ANTHROPIC_MODEL,
            base_url=base_url or ANTHROPIC_URL,
            timeout_seconds=timeout_seconds,
        )
    if provider == "openai":
        if not model:
            raise ValueError("FROBI_LLM_MODEL is required for an OpenAI-compatible provider")
        return OpenAiCompatibleLlmClient(
            api_key=api_key,
            model=model,
            base_url=base_url or OPENAI_URL,
            timeout_seconds=timeout_seconds,
        )
    raise ValueError(f"Unknown FROBI_LLM_PROVIDER: {provider!r} (use anthropic or openai)")
