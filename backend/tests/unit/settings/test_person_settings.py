from uuid import uuid4

import pytest

from frobi.modules.settings.domain import (
    IntroStatus,
    Language,
    LanguageNotAvailable,
    PersonSettings,
    UnknownSetting,
)


@pytest.fixture
def settings() -> PersonSettings:
    return PersonSettings.defaults(uuid4())


def test_defaults_are_all_off_spanish_and_wizard_pending(settings: PersonSettings) -> None:
    assert settings.enabled == frozenset()
    assert settings.language is Language.ES
    assert settings.intro_status is IntroStatus.PENDING
    assert settings.onboarding_done is False


def test_switch_only_changes_what_is_sent(settings: PersonSettings) -> None:
    on = settings.switch({"voice": True, "captions": True})

    off = on.switch({"voice": False})

    assert off.enabled_in_order() == ["captions"]


def test_switch_rejects_unknown_names(settings: PersonSettings) -> None:
    with pytest.raises(UnknownSetting):
        settings.switch({"dark_mode": True})


def test_only_spanish_is_available_for_now(settings: PersonSettings) -> None:
    assert settings.speak(Language.ES).language is Language.ES
    with pytest.raises(LanguageNotAvailable):
        settings.speak(Language.QU)


def test_onboarding_sets_exactly_the_given_switches(settings: PersonSettings) -> None:
    before = settings.switch({"keyboard_mode": True})

    after = before.after_onboarding(
        profiles=["reading", "reading", "hearing"],
        enabled=["short_texts", "voice", "captions"],
        intro_status=IntroStatus.SEEN,
        done=True,
    )

    assert after.profiles == ("reading", "hearing")
    assert after.enabled_in_order() == ["voice", "short_texts", "captions"]
    assert after.onboarding_done is True
