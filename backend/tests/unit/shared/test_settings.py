import pytest

from frobi.shared.infrastructure import Settings


def test_cors_origins_accept_a_comma_separated_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FROBI_CORS_ORIGINS", "http://localhost:5173, https://frobi.demo/")

    settings = Settings(_env_file=None)

    assert settings.cors_origins == ["http://localhost:5173", "https://frobi.demo"]


def test_llm_key_is_never_shown_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FROBI_LLM_API_KEY", "sk-secret")

    settings = Settings(_env_file=None)

    assert "sk-secret" not in repr(settings)
    assert settings.llm_api_key is not None
    assert settings.llm_api_key.get_secret_value() == "sk-secret"
