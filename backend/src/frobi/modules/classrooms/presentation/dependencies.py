"""Wiring: builds classrooms' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.classrooms.application import (
    CreateClassHandler,
    DashboardHandler,
    GetClassHandler,
    InviteStudentsHandler,
    JoinClassHandler,
    JoinWithCodeHandler,
    ListClassContentHandler,
    ListMembersHandler,
    ListMyClassesHandler,
    StudentDetailHandler,
    UploadClassContentHandler,
)
from frobi.modules.classrooms.domain import new_invite_code
from frobi.modules.classrooms.infrastructure import (
    ClassActivityReaderAdapter,
    ClassMaterialsAdapter,
    PersonDirectoryAdapter,
    SqlAlchemyClassRepository,
    SqlAlchemyMembershipRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_settings

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


def get_dashboard(db: DbSession) -> DashboardHandler:
    return DashboardHandler(
        SqlAlchemyClassRepository(db),
        SqlAlchemyMembershipRepository(db),
        PersonDirectoryAdapter(db),
        ClassActivityReaderAdapter(db),
    )


def get_student_detail(db: DbSession) -> StudentDetailHandler:
    return StudentDetailHandler(
        SqlAlchemyClassRepository(db),
        SqlAlchemyMembershipRepository(db),
        PersonDirectoryAdapter(db),
        ClassActivityReaderAdapter(db),
    )


def get_join_class(db: DbSession, clock: AppClock) -> JoinWithCodeHandler:
    join = JoinClassHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyClassRepository(db),
        SqlAlchemyMembershipRepository(db),
        clock,
    )
    return JoinWithCodeHandler(join, PersonDirectoryAdapter(db))


def get_upload_class_content(
    db: DbSession,
    llm: Annotated[LlmClient, Depends(get_llm)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UploadClassContentHandler:
    return UploadClassContentHandler(
        SqlAlchemyClassRepository(db),
        ClassMaterialsAdapter(db, llm, settings.llm_timeout_seconds),
    )


def get_list_class_content(db: DbSession) -> ListClassContentHandler:
    return ListClassContentHandler(get_get_class(db), ClassMaterialsAdapter(db))


def get_list_my_classes(db: DbSession) -> ListMyClassesHandler:
    return ListMyClassesHandler(SqlAlchemyClassRepository(db), PersonDirectoryAdapter(db))
