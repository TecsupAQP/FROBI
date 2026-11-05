"""Public API of identity: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.infrastructure import SqlAlchemyUnitOfWork

from .application import ConfigurePersonHandler, ReadPersonHandler
from .domain import ConfiguredBy, Person, Role


def configure_person_handler(session: AsyncSession) -> ConfigurePersonHandler:
    from .infrastructure import SqlAlchemyPersonRepository

    return ConfigurePersonHandler(
        SqlAlchemyUnitOfWork(session), SqlAlchemyPersonRepository(session)
    )


def read_person_handler(session: AsyncSession) -> ReadPersonHandler:
    from .infrastructure import SqlAlchemyPersonRepository

    return ReadPersonHandler(SqlAlchemyPersonRepository(session))


__all__ = [
    "ConfigurePersonHandler",
    "ConfiguredBy",
    "Person",
    "ReadPersonHandler",
    "Role",
    "configure_person_handler",
    "read_person_handler",
]
