import pytest
from pydantic import SecretStr

from frobi.modules.assistant.infrastructure import (
    ClaudeAssistant,
    DisabledAssistant,
    assistant_enabled,
    build_assistant,
)
from frobi.shared.infrastructure import Settings


@pytest.mark.parametrize(
    ("provider", "key"),
    [("anthropic", None), ("anthropic", ""), ("anthropic", "   "), ("openai", "sk-x")],
)
def test_without_an_anthropic_key_the_assistant_is_off(provider: str, key: str | None) -> None:
    settings = Settings(
        _env_file=None,
        llm_provider=provider,  # type: ignore[arg-type]
        llm_api_key=None if key is None else SecretStr(key),
    )

    assert not assistant_enabled(settings)
    assert isinstance(build_assistant(settings), DisabledAssistant)


def test_with_a_key_it_is_claude() -> None:
    settings = Settings(_env_file=None, llm_api_key=SecretStr("sk-ant-test"))

    assert assistant_enabled(settings)
    assert isinstance(build_assistant(settings), ClaudeAssistant)
