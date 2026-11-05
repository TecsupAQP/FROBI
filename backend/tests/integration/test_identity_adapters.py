from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.identity.domain import Person, Role
from frobi.modules.identity.infrastructure import (
    SESSION_TTL,
    RedisSessionStore,
    SqlAlchemyPersonRepository,
)

pytestmark = pytest.mark.integration

NOW = datetime(2026, 11, 5, 9, 0, tzinfo=UTC)


async def test_person_round_trips_through_postgres(db_session: AsyncSession) -> None:
    repository = SqlAlchemyPersonRepository(db_session)
    person = Person.register(alias="Ana", career="Mecatrónica", role=Role.TEACHER, now=NOW)

    await repository.add(person)
    await db_session.commit()
    db_session.expunge_all()

    assert await repository.get(person.id) == person


async def test_unknown_person_is_none(db_session: AsyncSession) -> None:
    assert await SqlAlchemyPersonRepository(db_session).get(uuid4()) is None


async def test_database_rejects_an_unknown_role(db_session: AsyncSession) -> None:
    with pytest.raises(IntegrityError):
        await db_session.execute(
            text(
                "INSERT INTO persons (id, alias, career, role, configured_by, created_at) "
                "VALUES (:id, 'Ana', 'Mecatrónica', 'admin', 'self', now())"
            ),
            {"id": uuid4()},
        )


async def test_session_resolves_until_revoked(redis: "Redis") -> None:
    store = RedisSessionStore(redis)
    person_id = uuid4()

    token = await store.create(person_id)
    resolved = await store.resolve(token)
    await store.revoke(token)

    assert resolved == person_id
    assert await store.resolve(token) is None


async def test_session_lives_30_days(redis: "Redis") -> None:
    token = await RedisSessionStore(redis).create(uuid4())

    ttl = await redis.ttl(f"session:{token}")

    assert SESSION_TTL - timedelta(seconds=5) <= timedelta(seconds=ttl) <= SESSION_TTL


async def test_tokens_are_long_and_unique(redis: "Redis") -> None:
    store = RedisSessionStore(redis)

    tokens = {await store.create(uuid4()) for _ in range(20)}

    assert len(tokens) == 20
    assert all(len(token) >= 40 for token in tokens)


async def test_garbage_in_a_session_key_is_no_session(redis: "Redis") -> None:
    await redis.set("session:broken", "not-a-uuid")

    assert await RedisSessionStore(redis).resolve("broken") is None
