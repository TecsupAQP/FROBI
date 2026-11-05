"""Public API of identity: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.infrastructure import SqlAlchemyUnitOfWork

from .application import ConfigurePersonHandler
from .domain import ConfiguredBy


def configure_person_handler(session: AsyncSession) -> ConfigurePersonHandler:
    from .infrastructure import SqlAlchemyPersonRepository

    return ConfigurePersonHandler(
        SqlAlchemyUnitOfWork(session), SqlAlchemyPersonRepository(session)
    )


__all__ = ["ConfigurePersonHandler", "ConfiguredBy", "configure_person_handler"]
