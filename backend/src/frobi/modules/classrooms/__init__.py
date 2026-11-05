"""Public API of classrooms: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.infrastructure import SqlAlchemyUnitOfWork, SystemClock

from .application import (
    ActiveClass,
    ActiveClassHandler,
    DashboardHandler,
    JoinClassHandler,
    LeaveClassHandler,
    ListMyClassesHandler,
    Panel,
    StudentDetail,
    StudentDetailHandler,
)
from .application.demo import DEMO_PEOPLE, DemoPeopleHandler
from .domain import Classroom


def join_class_handler(session: AsyncSession) -> JoinClassHandler:
    """``find_by_code`` and ``join`` / ``handle`` (code) for a person (identity, settings)."""
    from .infrastructure import SqlAlchemyClassRepository, SqlAlchemyMembershipRepository

    return JoinClassHandler(
        SqlAlchemyUnitOfWork(session),
        SqlAlchemyClassRepository(session),
        SqlAlchemyMembershipRepository(session),
        SystemClock(),
    )


def active_class_handler(session: AsyncSession) -> ActiveClassHandler:
    from .infrastructure import SqlAlchemyClassRepository, SqlAlchemyMembershipRepository

    return ActiveClassHandler(
        SqlAlchemyClassRepository(session), SqlAlchemyMembershipRepository(session)
    )


def demo_people_handler(session: AsyncSession) -> DemoPeopleHandler:
    """``person_for("teacher" | "ana" | "luis")`` in the seeded demo class (identity)."""
    from .infrastructure import SqlAlchemyMembershipRepository

    return DemoPeopleHandler(SqlAlchemyMembershipRepository(session))


def leave_class_handler(session: AsyncSession) -> LeaveClassHandler:
    from .infrastructure import SqlAlchemyMembershipRepository

    return LeaveClassHandler(
        SqlAlchemyUnitOfWork(session), SqlAlchemyMembershipRepository(session), SystemClock()
    )


def my_classes_handler(session: AsyncSession) -> ListMyClassesHandler:
    """The classes a teacher teaches; anyone else gets ``TeachersOnly`` (assistant)."""
    from .infrastructure import PersonDirectoryAdapter, SqlAlchemyClassRepository

    return ListMyClassesHandler(SqlAlchemyClassRepository(session), PersonDirectoryAdapter(session))


def dashboard_handler(session: AsyncSession) -> DashboardHandler:
    """Teacher panel of one of their classes; only activity made inside it (assistant)."""
    from .infrastructure import (
        ClassActivityReaderAdapter,
        PersonDirectoryAdapter,
        SqlAlchemyClassRepository,
        SqlAlchemyMembershipRepository,
    )

    return DashboardHandler(
        SqlAlchemyClassRepository(session),
        SqlAlchemyMembershipRepository(session),
        PersonDirectoryAdapter(session),
        ClassActivityReaderAdapter(session),
    )


def student_detail_handler(session: AsyncSession) -> StudentDetailHandler:
    """One student of the teacher's class; only activity of that class (assistant)."""
    from .infrastructure import (
        ClassActivityReaderAdapter,
        PersonDirectoryAdapter,
        SqlAlchemyClassRepository,
        SqlAlchemyMembershipRepository,
    )

    return StudentDetailHandler(
        SqlAlchemyClassRepository(session),
        SqlAlchemyMembershipRepository(session),
        PersonDirectoryAdapter(session),
        ClassActivityReaderAdapter(session),
    )


__all__ = [
    "DEMO_PEOPLE",
    "ActiveClass",
    "ActiveClassHandler",
    "Classroom",
    "DashboardHandler",
    "DemoPeopleHandler",
    "JoinClassHandler",
    "LeaveClassHandler",
    "ListMyClassesHandler",
    "Panel",
    "StudentDetail",
    "StudentDetailHandler",
    "active_class_handler",
    "demo_people_handler",
    "join_class_handler",
    "leave_class_handler",
]
