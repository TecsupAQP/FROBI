from datetime import UTC, datetime

import pytest

from frobi.modules.identity.domain import (
    ConfiguredBy,
    InvalidAlias,
    InvalidCareer,
    Person,
    Role,
)

NOW = datetime(2026, 11, 5, 9, 0, tzinfo=UTC)


def test_register_trims_and_collapses_spaces() -> None:
    person = Person.register(
        alias="  Ana   María ", career=" Mecatrónica ", role=Role.LEARNER, now=NOW
    )

    assert person.alias == "Ana María"
    assert person.career == "Mecatrónica"
    assert person.configured_by is ConfiguredBy.SELF
    assert person.created_at == NOW


def test_each_registration_gets_its_own_id() -> None:
    first = Person.register(alias="Ana", career="Mecatrónica", role=Role.LEARNER, now=NOW)
    second = Person.register(alias="Ana", career="Mecatrónica", role=Role.LEARNER, now=NOW)

    assert first.id != second.id


@pytest.mark.parametrize("alias", ["", "   ", "x" * 41])
def test_alias_must_have_1_to_40_visible_characters(alias: str) -> None:
    with pytest.raises(InvalidAlias):
        Person.register(alias=alias, career="Mecatrónica", role=Role.LEARNER, now=NOW)


@pytest.mark.parametrize("career", ["  ", "x" * 81])
def test_career_must_have_1_to_80_visible_characters(career: str) -> None:
    with pytest.raises(InvalidCareer):
        Person.register(alias="Ana", career=career, role=Role.TEACHER, now=NOW)
