from uuid import UUID

import pytest

from fakes.identity import IdentityFakes
from frobi.modules.identity.application import DemoSessionHandler
from frobi.modules.identity.domain import DemoNotSeeded, DemoUnavailable, Person, Role


class Demo:
    def __init__(self, people: dict[str, UUID]) -> None:
        self.people = people

    async def person_for(self, who: str) -> UUID | None:
        return self.people.get(who)


def _handler(fakes: IdentityFakes, demo: Demo, *, enabled: bool = True) -> DemoSessionHandler:
    return DemoSessionHandler(
        fakes.persons, fakes.sessions, fakes.memberships, demo, enabled=enabled
    )


async def _person(fakes: IdentityFakes, alias: str, role: Role) -> Person:
    person = Person.register(
        alias=alias, career="Instrumentación", role=role, now=fakes.clock.now()
    )
    await fakes.persons.add(person)
    return person


async def test_enters_as_the_existing_demo_person_without_creating_one() -> None:
    fakes = IdentityFakes()
    teacher = await _person(fakes, "Docente demo", Role.TEACHER)

    result = await _handler(fakes, Demo({"teacher": teacher.id})).handle("teacher")

    assert result.person == teacher
    assert fakes.sessions.tokens[result.token] == teacher.id
    assert list(fakes.persons.items) == [teacher.id]


async def test_a_student_not_seeded_yet_says_to_run_the_seed() -> None:
    with pytest.raises(DemoNotSeeded):
        await _handler(IdentityFakes(), Demo({})).handle("ana")


async def test_outside_local_or_demo_the_demo_sign_in_does_not_exist() -> None:
    fakes = IdentityFakes()
    teacher = await _person(fakes, "Docente demo", Role.TEACHER)

    with pytest.raises(DemoUnavailable):
        await _handler(fakes, Demo({"teacher": teacher.id}), enabled=False).handle("teacher")
    assert fakes.sessions.tokens == {}
