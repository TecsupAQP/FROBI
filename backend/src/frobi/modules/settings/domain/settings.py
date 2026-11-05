"""A person's accessibility switches, language and wizard state (M2, M13)."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum
from uuid import UUID

from .errors import LanguageNotAvailable, UnknownSetting

TOGGLES: tuple[str, ...] = (
    "voice",
    "high_contrast",
    "large_text",
    "short_texts",
    "captions",
    "large_buttons",
    "keyboard_mode",
)


class Language(StrEnum):
    ES = "es"
    QU = "qu"
    AY = "ay"


AVAILABLE_LANGUAGES = frozenset({Language.ES})


class IntroStatus(StrEnum):
    SEEN = "seen"
    SKIPPED = "skipped"
    PENDING = "pending"


def _known(names: Iterable[str]) -> frozenset[str]:
    names = frozenset(names)
    unknown = names - set(TOGGLES)
    if unknown:
        raise UnknownSetting(f"Ajuste desconocido: {', '.join(sorted(unknown))}.")
    return names


@dataclass(frozen=True, slots=True)
class PersonSettings:
    person_id: UUID
    profiles: tuple[str, ...] = ()
    enabled: frozenset[str] = field(default_factory=frozenset)
    language: Language = Language.ES
    intro_status: IntroStatus = IntroStatus.PENDING
    onboarding_done: bool = False

    @classmethod
    def defaults(cls, person_id: UUID) -> "PersonSettings":
        return cls(person_id=person_id)

    def is_on(self, toggle: str) -> bool:
        return toggle in self.enabled

    def enabled_in_order(self) -> list[str]:
        return [toggle for toggle in TOGGLES if toggle in self.enabled]

    def switch(self, changes: Mapping[str, bool]) -> "PersonSettings":
        _known(changes)
        enabled = {t for t in self.enabled if changes.get(t, True)}
        enabled |= {t for t, on in changes.items() if on}
        return replace(self, enabled=frozenset(enabled))

    def speak(self, language: Language) -> "PersonSettings":
        if language not in AVAILABLE_LANGUAGES:
            raise LanguageNotAvailable()
        return replace(self, language=language)

    def after_onboarding(
        self,
        *,
        profiles: Iterable[str],
        enabled: Iterable[str],
        intro_status: IntroStatus,
        done: bool,
    ) -> "PersonSettings":
        return replace(
            self,
            profiles=tuple(dict.fromkeys(profiles)),
            enabled=_known(enabled),
            intro_status=intro_status,
            onboarding_done=done,
        )
