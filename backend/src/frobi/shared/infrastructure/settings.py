"""Runtime configuration, read from ``FROBI_*`` environment variables (or a local ``.env``)."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FROBI_", env_file=".env", extra="ignore")

    environment: str = "local"
    database_url: str = "postgresql+asyncpg://frobi:frobi@localhost:5432/frobi"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )
    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: float = Field(default=15.0, gt=0)
    llm_requests_per_minute: int = Field(default=10, ge=1)
    health_timeout_seconds: float = Field(default=2.0, gt=0)
    # Cloudflare R2 (S3 API) for the original PDFs. Without keys uploads keep only their text.
    r2_endpoint: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: SecretStr | None = None
    r2_bucket: str = "frobi"
    r2_signed_url_seconds: int = Field(default=900, ge=60, le=604_800)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_comma_separated(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
