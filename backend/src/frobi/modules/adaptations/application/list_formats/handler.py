"""The 4 formats, marking the one suggested by the person's profile (RF03, RF35)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.adaptations.application.ports import ProfileReader
from frobi.modules.adaptations.domain import FORMATS, FormatInfo, suggested_format


@dataclass(frozen=True, slots=True)
class FormatOption:
    info: FormatInfo
    suggested: bool


class ListFormatsHandler:
    def __init__(self, profiles: ProfileReader) -> None:
        self._profiles = profiles

    async def handle(self, person_id: UUID) -> list[FormatOption]:
        profile = await self._profiles.for_person(person_id)
        suggested = suggested_format(profile.enabled_settings)
        return [FormatOption(info=f, suggested=f.id is suggested) for f in FORMATS]
