from frobi.modules.assistant.application.ports import AssistantModel
from frobi.shared.infrastructure import Settings

from .claude_assistant import ClaudeAssistant, DisabledAssistant


def _api_key(settings: Settings) -> str | None:
    """The Anthropic key, or None when the provider is another one or the key is blank."""
    if settings.llm_provider != "anthropic" or settings.llm_api_key is None:
        return None
    return settings.llm_api_key.get_secret_value().strip() or None


def assistant_enabled(settings: Settings) -> bool:
    return _api_key(settings) is not None


def build_assistant(settings: Settings) -> AssistantModel:
    """Claude when there is an Anthropic key; otherwise every answer is the fallback (RNF03)."""
    api_key = _api_key(settings)
    if api_key is None:
        return DisabledAssistant()
    return ClaudeAssistant(
        api_key=api_key, model=settings.assistant_model, effort=settings.assistant_effort
    )
