from typing import Any, Protocol


class LlmUnavailable(Exception):
    """No provider configured, or the provider refused or failed the call."""


class LlmClient(Protocol):
    async def complete_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        """Ask the model for a JSON object. Callers validate its shape."""
        ...


class DisabledLlmClient:
    """Used while no provider is chosen: every call goes straight to the fallback."""

    async def complete_json(self, *, system: str, prompt: str) -> dict[str, Any]:
        raise LlmUnavailable("No AI provider configured")
