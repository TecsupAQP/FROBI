from uuid import uuid4

import pytest

from fakes.onboarding import FakePersonConfigurator, FakeSettingsWriter
from frobi.modules.onboarding.application import (
    CompleteOnboardingCommand,
    CompleteOnboardingHandler,
    ResetOnboardingHandler,
    SkipOnboardingHandler,
)
from frobi.modules.onboarding.domain import (
    CATALOGUE,
    AccessibilityProfile,
    AccessibilitySetting,
    WhoUses,
    settings_for,
)

P = AccessibilityProfile
S = AccessibilitySetting
PERSON = uuid4()


def test_every_profile_turns_on_at_least_one_setting() -> None:
    assert {profile.id for profile in CATALOGUE} == set(AccessibilityProfile)
    assert all(profile.enables for profile in CATALOGUE)


def test_settings_of_several_profiles_are_merged_without_duplicates() -> None:
    assert settings_for([P.READING, P.LOW_VISION]) == (
        S.VOICE,
        S.HIGH_CONTRAST,
        S.LARGE_TEXT,
        S.SHORT_TEXTS,
    )


def test_no_profile_turns_nothing_on() -> None:
    assert settings_for([]) == ()


@pytest.fixture
def writer() -> FakeSettingsWriter:
    return FakeSettingsWriter()


@pytest.fixture
def persons() -> FakePersonConfigurator:
    return FakePersonConfigurator()


async def test_complete_records_profiles_switches_and_who_set_it_up(
    writer: FakeSettingsWriter, persons: FakePersonConfigurator
) -> None:
    result = await CompleteOnboardingHandler(writer, persons).handle(
        CompleteOnboardingCommand(
            person_id=PERSON,
            who_uses=WhoUses.COMPANION,
            profiles=(P.MOTOR, P.MOTOR, P.HEARING),
            intro="seen",
        )
    )

    assert persons.by[PERSON] is WhoUses.COMPANION
    assert result.done is True
    assert result.profiles == ("motor", "hearing")
    assert result.enabled_settings == ("captions", "large_buttons", "keyboard_mode")
    assert result.intro_status == "seen"


async def test_skip_finishes_the_wizard_and_keeps_the_switches(
    persons: FakePersonConfigurator,
) -> None:
    writer = FakeSettingsWriter(enabled=("voice",))

    result = await SkipOnboardingHandler(writer, persons).handle(PERSON)

    assert writer.calls[-1]["enabled"] is None
    assert result.done is True
    assert result.intro_status == "skipped"
    assert result.enabled_settings == ("voice",)
    assert result.configured_by is WhoUses.SELF


async def test_reset_reopens_the_wizard(
    writer: FakeSettingsWriter, persons: FakePersonConfigurator
) -> None:
    result = await ResetOnboardingHandler(writer, persons).handle(PERSON)

    assert result.done is False
    assert result.intro_status == "pending"
    assert result.profiles == ()
