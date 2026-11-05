from collections.abc import Mapping
from dataclasses import dataclass, field
from uuid import UUID

from frobi.modules.settings.domain import Language


@dataclass(frozen=True, slots=True)
class UpdateSettingsCommand:
    person_id: UUID
    toggles: Mapping[str, bool] = field(default_factory=dict)
    language: Language | None = None
