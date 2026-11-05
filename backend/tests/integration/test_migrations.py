"""The ORM models and the Alembic migrations must describe the same schema."""

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from frobi.models import metadata

pytestmark = pytest.mark.integration


def _diff(connection: Connection) -> list[object]:
    context = MigrationContext.configure(connection, opts={"compare_type": True})
    return list(compare_metadata(context, metadata))


async def test_models_match_the_migrations(migrated_database: str) -> None:
    engine = create_async_engine(migrated_database)
    async with engine.connect() as connection:
        diff = await connection.run_sync(_diff)
    await engine.dispose()

    assert diff == [], "Models changed without a migration: run `uv run alembic revision -m ...`"
