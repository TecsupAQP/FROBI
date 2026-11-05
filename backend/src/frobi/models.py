"""Registers every module's ORM models on ``Base.metadata`` (for Alembic and test setup).

Add a module's ``infrastructure.models`` here when it gets its first table.
"""

from frobi.modules.identity.infrastructure import models as identity_models
from frobi.modules.materials.infrastructure import models as materials_models
from frobi.modules.settings.infrastructure import models as settings_models
from frobi.shared.infrastructure import Base

metadata = Base.metadata

__all__ = ["identity_models", "materials_models", "metadata", "settings_models"]
