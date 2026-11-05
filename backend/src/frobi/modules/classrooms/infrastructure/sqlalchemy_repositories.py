from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.classrooms.domain import Classroom, Membership, MembershipStatus

from .models import ClassModel, MembershipModel


def _classroom(row: ClassModel) -> Classroom:
    return Classroom(
        id=row.id,
        teacher_id=row.teacher_id,
        name=row.name,
        subject=row.subject,
        tasks=tuple(str(t) for t in row.tasks),
        invite_code=row.invite_code,
        created_at=row.created_at,
    )


def _membership(row: MembershipModel) -> Membership:
    return Membership(
        id=row.id,
        class_id=row.class_id,
        person_id=row.person_id,
        alias=row.alias,
        status=MembershipStatus(row.status),
        created_at=row.created_at,
        joined_at=row.joined_at,
        left_at=row.left_at,
    )


class SqlAlchemyClassRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, classroom: Classroom) -> None:
        self._session.add(
            ClassModel(
                id=classroom.id,
                teacher_id=classroom.teacher_id,
                name=classroom.name,
                subject=classroom.subject,
                tasks=list(classroom.tasks),
                invite_code=classroom.invite_code,
                created_at=classroom.created_at,
            )
        )

    async def get(self, class_id: UUID) -> Classroom | None:
        row = await self._session.get(ClassModel, class_id)
        return None if row is None else _classroom(row)

    async def list_for_teacher(self, teacher_id: UUID) -> list[Classroom]:
        query = (
            select(ClassModel)
            .where(ClassModel.teacher_id == teacher_id)
            .order_by(ClassModel.created_at.desc())
        )
        return [_classroom(row) for row in (await self._session.scalars(query)).all()]

    async def get_by_code(self, code: str) -> Classroom | None:
        row = await self._session.scalar(select(ClassModel).where(ClassModel.invite_code == code))
        return None if row is None else _classroom(row)

    async def code_taken(self, code: str) -> bool:
        return bool(
            await self._session.scalar(select(exists().where(ClassModel.invite_code == code)))
        )


class SqlAlchemyMembershipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, membership: Membership) -> None:
        self._session.add(
            MembershipModel(
                id=membership.id,
                class_id=membership.class_id,
                person_id=membership.person_id,
                alias=membership.alias,
                status=membership.status.value,
                created_at=membership.created_at,
                joined_at=membership.joined_at,
                left_at=membership.left_at,
            )
        )
        await self._session.flush()

    async def save(self, membership: Membership) -> None:
        row = await self._session.get(MembershipModel, membership.id)
        if row is None:
            await self.add(membership)
            return
        row.person_id = membership.person_id
        row.alias = membership.alias
        row.status = membership.status.value
        row.joined_at = membership.joined_at
        row.left_at = membership.left_at
        # Flush now so «leave the old class» lands before «join the new one» (one joined max).
        await self._session.flush()

    async def active_for(self, person_id: UUID) -> Membership | None:
        row = await self._session.scalar(
            select(MembershipModel).where(
                MembershipModel.person_id == person_id,
                MembershipModel.status == MembershipStatus.JOINED.value,
            )
        )
        return None if row is None else _membership(row)

    async def for_class(self, class_id: UUID) -> list[Membership]:
        query = (
            select(MembershipModel)
            .where(MembershipModel.class_id == class_id)
            .order_by(MembershipModel.created_at, MembershipModel.alias)
        )
        return [_membership(row) for row in (await self._session.scalars(query)).all()]
