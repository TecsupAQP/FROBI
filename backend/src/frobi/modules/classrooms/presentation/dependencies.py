"""Wiring: builds classrooms' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.classrooms.application import (
    CreateClassHandler,
    GetClassHandler,
    InviteStudentsHandler,
    JoinClassHandler,
    JoinWithCodeHandler,
    ListMembersHandler,
)
from frobi.modules.classrooms.domain import new_invite_code
from frobi.modules.classrooms.infrastructure import (
    PersonDirectoryAdapter,
    SqlAlchemyClassRepository,
    SqlAlchemyMembershipRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import SqlAlchemyUnitOfWork
from frobi.shared.presentation import get_clock, get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppClock = Annotated[Clock, Depends(get_clock)]


def get_create_class(db: DbSession, clock: AppClock) -> CreateClassHandler:
    return CreateClassHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyClassRepository(db),
        PersonDirectoryAdapter(db),
        new_invite_code,
        clock,
    )


def get_get_class(db: DbSession) -> GetClassHandler:
    return GetClassHandler(SqlAlchemyClassRepository(db), SqlAlchemyMembershipRepository(db))


def get_invite_students(db: DbSession, clock: AppClock) -> InviteStudentsHandler:
    return InviteStudentsHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyClassRepository(db),
        SqlAlchemyMembershipRepository(db),
        clock,
    )


def get_list_members(db: DbSession) -> ListMembersHandler:
    return ListMembersHandler(SqlAlchemyClassRepository(db), SqlAlchemyMembershipRepository(db))


def get_join_class(db: DbSession, clock: AppClock) -> JoinWithCodeHandler:
    join = JoinClassHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyClassRepository(db),
        SqlAlchemyMembershipRepository(db),
        clock,
    )
    return JoinWithCodeHandler(join, PersonDirectoryAdapter(db))
