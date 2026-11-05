"""Real Postgres and Redis from docker/compose.yml, isolated from the dev data.

- Postgres: a separate ``frobi_test`` database, migrated with Alembic once per run (this also
  checks that the migrations apply cleanly). Each test runs inside a transaction that is rolled
  back.
- Redis: database 15, flushed after each test.
"""

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from redis.asyncio import Redis
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from frobi.shared.infrastructure import Settings

BACKEND = Path(__file__).resolve().parents[2]
TEST_DB = "frobi_test"
TEST_REDIS_DB = 15


def _test_settings() -> Settings:
    base = Settings()
    url = make_url(base.database_url).set(database=TEST_DB)
    redis_url = base.redis_url.rsplit("/", 1)[0] + f"/{TEST_REDIS_DB}"
    return Settings(
        _env_file=None,
        database_url=url.render_as_string(hide_password=False),
        redis_url=redis_url,
        llm_api_key=None,  # tests never call a real AI provider
    )


async def _create_database_if_missing(database_url: str) -> None:
    url = make_url(database_url)
    connection = await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database="postgres",
    )
    try:
        exists = await connection.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB)
        if not exists:
            await connection.execute(f'CREATE DATABASE "{TEST_DB}"')
    finally:
        await connection.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return _test_settings()


@pytest.fixture(scope="session")
def migrated_database(test_settings: Settings) -> str:
    asyncio.run(_create_database_if_missing(test_settings.database_url))
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", test_settings.database_url)
    config.attributes["configure_logger"] = False
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    return test_settings.database_url


@pytest.fixture
async def db_session(migrated_database: str) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(migrated_database)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest.fixture
async def redis(test_settings: Settings) -> AsyncIterator["Redis"]:
    client: Redis = Redis.from_url(test_settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.flushdb()
        await client.aclose()
