from typing import Protocol
from uuid import UUID

from frobi.modules.settings.domain import PersonSettings


class SettingsRepository(Protocol):
    async def get(self, person_id: UUID) -> PersonSettings | None: ...

    async def save(self, settings: PersonSettings) -> None: ...


__all__ = ["SettingsRepository"]
