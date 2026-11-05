"""Registers every module's ORM models on ``Base.metadata`` (for Alembic and test setup).

Add a module's ``infrastructure.models`` here when it gets its first table.
"""

from frobi.modules.adaptations.infrastructure import models as adaptations_models
from frobi.modules.identity.infrastructure import models as identity_models
from frobi.modules.materials.infrastructure import models as materials_models
from frobi.modules.prompt_coach.infrastructure import models as prompt_coach_models
from frobi.modules.settings.infrastructure import models as settings_models
from frobi.modules.tutoring.infrastructure import models as tutoring_models
from frobi.shared.infrastructure import Base

metadata = Base.metadata

__all__ = [
    "adaptations_models",
    "identity_models",
    "materials_models",
    "metadata",
    "prompt_coach_models",
    "settings_models",
    "tutoring_models",
]
