"""Wiring: builds classrooms' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.classrooms.application import (
    ClassGuidesProgressHandler,
    CreateClassHandler,
    DashboardHandler,
    GetClassHandler,
    InviteStudentsHandler,
    JoinClassHandler,
    JoinWithCodeHandler,
    ListClassContentHandler,
    ListClassGuidesHandler,
    ListMembersHandler,
    ListMyClassesHandler,
    MyGuidesProgressHandler,
    SaveGuidePlanHandler,
    StudentDetailHandler,
    UploadClassContentHandler,
)
from frobi.modules.classrooms.domain import new_invite_code
from frobi.modules.classrooms.infrastructure import (
    ClassActivityReaderAdapter,
    ClassMaterialsAdapter,
    GuideActivityReaderAdapter,
    PersonDirectoryAdapter,
    SqlAlchemyClassRepository,
    SqlAlchemyGuidePlanRepository,
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


def get_upload_class_content(db: DbSession) -> UploadClassContentHandler:
    return UploadClassContentHandler(SqlAlchemyClassRepository(db), ClassMaterialsAdapter(db))


def get_list_class_content(db: DbSession) -> ListClassContentHandler:
    return ListClassContentHandler(get_get_class(db), ClassMaterialsAdapter(db))


def get_list_my_classes(db: DbSession) -> ListMyClassesHandler:
    return ListMyClassesHandler(SqlAlchemyClassRepository(db), PersonDirectoryAdapter(db))


def get_save_guide_plan(db: DbSession) -> SaveGuidePlanHandler:
    return SaveGuidePlanHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyClassRepository(db),
        ClassMaterialsAdapter(db),
        SqlAlchemyGuidePlanRepository(db),
    )


def get_list_class_guides(db: DbSession) -> ListClassGuidesHandler:
    return ListClassGuidesHandler(
        get_get_class(db), ClassMaterialsAdapter(db), SqlAlchemyGuidePlanRepository(db)
    )


def get_my_guides_progress(db: DbSession) -> MyGuidesProgressHandler:
    return MyGuidesProgressHandler(
        get_get_class(db),
        ClassMaterialsAdapter(db),
        SqlAlchemyGuidePlanRepository(db),
        GuideActivityReaderAdapter(db),
    )


def get_class_guides_progress(db: DbSession) -> ClassGuidesProgressHandler:
    return ClassGuidesProgressHandler(
        SqlAlchemyClassRepository(db),
        SqlAlchemyMembershipRepository(db),
        PersonDirectoryAdapter(db),
        ClassMaterialsAdapter(db),
        SqlAlchemyGuidePlanRepository(db),
        GuideActivityReaderAdapter(db),
    )
