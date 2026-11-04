"""Runtime configuration, read from ``FROBI_*`` environment variables (or a local ``.env``)."""

from functools import lru_cache
from typing import Annotated

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
    llm_api_key: SecretStr | None = None
    llm_timeout_seconds: float = Field(default=15.0, gt=0)
    health_timeout_seconds: float = Field(default=2.0, gt=0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_comma_separated(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
