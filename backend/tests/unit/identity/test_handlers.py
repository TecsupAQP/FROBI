import pytest

from fakes.identity import EXAMPLE_CLASS, IdentityFakes
from frobi.modules.identity.application import StartSessionCommand
from frobi.modules.identity.domain import InvalidAlias, InvalidClassCode, Role
from frobi.shared.application import Unauthenticated


@pytest.fixture
def fakes() -> IdentityFakes:
    return IdentityFakes()


async def test_entering_creates_the_person_and_a_session(fakes: IdentityFakes) -> None:
    result = await fakes.start_session().handle(
        StartSessionCommand(alias="Ana", career="Mecatrónica", role=Role.LEARNER)
    )

    assert fakes.persons.items[result.person.id].alias == "Ana"
    assert await fakes.sessions.resolve(result.token) == result.person.id
    assert result.membership is None
    assert fakes.uow.commits == 1


async def test_entering_with_a_valid_code_joins_the_class(fakes: IdentityFakes) -> None:
    result = await fakes.start_session().handle(
        StartSessionCommand(
            alias="Ana", career="Mecatrónica", role=Role.LEARNER, class_code="sensor1"
        )
    )

    assert result.membership is not None
    assert result.membership.class_id == EXAMPLE_CLASS.id
    assert fakes.memberships.joined[result.person.id] == EXAMPLE_CLASS


async def test_a_blank_code_means_no_class(fakes: IdentityFakes) -> None:
    result = await fakes.start_session().handle(
        StartSessionCommand(alias="Ana", career="Mecatrónica", role=Role.LEARNER, class_code="  ")
    )

    assert result.membership is None


async def test_an_unknown_code_rejects_the_entry_and_creates_nothing(fakes: IdentityFakes) -> None:
    with pytest.raises(InvalidClassCode):
        await fakes.start_session().handle(
            StartSessionCommand(
                alias="Ana", career="Mecatrónica", role=Role.LEARNER, class_code="NOPE"
            )
        )

    assert fakes.persons.items == {}
    assert fakes.sessions.tokens == {}


async def test_an_invalid_alias_creates_nothing(fakes: IdentityFakes) -> None:
    with pytest.raises(InvalidAlias):
        await fakes.start_session().handle(
            StartSessionCommand(alias="   ", career="Mecatrónica", role=Role.LEARNER)
        )

    assert fakes.persons.items == {}


async def test_ending_the_session_invalidates_the_token(fakes: IdentityFakes) -> None:
    result = await fakes.start_session().handle(
        StartSessionCommand(alias="Ana", career="Mecatrónica", role=Role.LEARNER)
    )

    await fakes.end_session().handle(result.token)

    assert await fakes.sessions.resolve(result.token) is None


async def test_me_shows_person_class_and_wizard_state(fakes: IdentityFakes) -> None:
    result = await fakes.start_session().handle(
        StartSessionCommand(
            alias="Ana", career="Mecatrónica", role=Role.LEARNER, class_code="SENSOR1"
        )
    )

    view = await fakes.get_me().handle(result.person.id)

    assert view.person == result.person
    assert view.membership is not None
    assert view.membership.class_name == EXAMPLE_CLASS.name
    assert view.onboarding.done is False


async def test_me_for_a_person_that_no_longer_exists_is_unauthenticated(
    fakes: IdentityFakes,
) -> None:
    from uuid import uuid4

    with pytest.raises(Unauthenticated):
        await fakes.get_me().handle(uuid4())
