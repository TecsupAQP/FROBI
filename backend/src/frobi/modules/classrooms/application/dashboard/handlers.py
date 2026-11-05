"""Teacher panel and student detail. Only the class's teacher; only activity of this class."""

from dataclasses import replace
from uuid import UUID

from frobi.modules.classrooms.application.manage_class.handlers import own_class
from frobi.modules.classrooms.application.ports import (
    ClassActivityReader,
    ClassRepository,
    MembershipRepository,
    PersonDirectory,
)
from frobi.modules.classrooms.domain import (
    DEMO_CLASS_ID,
    ClassNotFound,
    MembershipStatus,
    TeachersOnly,
)

from .panel import Panel, StudentDetail, build_panel, build_student_detail, sample_panel


class DashboardHandler:
    def __init__(
        self,
        classes: ClassRepository,
        memberships: MembershipRepository,
        people: PersonDirectory,
        activity: ClassActivityReader,
    ) -> None:
        self._classes = classes
        self._memberships = memberships
        self._people = people
        self._activity = activity

    async def handle(self, teacher_id: UUID, class_id: UUID) -> Panel:
        if not await self._people.is_teacher(teacher_id):
            raise TeachersOnly()
        await own_class(self._classes, teacher_id, class_id)
        activity = await self._activity.read(class_id)
        if activity.empty:
            return sample_panel(class_id)
        members = await self._memberships.for_class(class_id)
        students = [
            (m.person_id, m.alias)
            for m in members
            if m.person_id is not None and m.status is MembershipStatus.JOINED
        ]
        panel = build_panel(class_id, students, activity)
        # The seeded demo class is all demo data, even once it has activity (RNF12, RNF18).
        return replace(panel, sample_data=True) if class_id == DEMO_CLASS_ID else panel


class StudentDetailHandler:
    def __init__(
        self,
        classes: ClassRepository,
        memberships: MembershipRepository,
        people: PersonDirectory,
        activity: ClassActivityReader,
    ) -> None:
        self._classes = classes
        self._memberships = memberships
        self._people = people
        self._activity = activity

    async def handle(self, teacher_id: UUID, class_id: UUID, person_id: UUID) -> StudentDetail:
        if not await self._people.is_teacher(teacher_id):
            raise TeachersOnly()
        await own_class(self._classes, teacher_id, class_id)
        member = next(
            (m for m in await self._memberships.for_class(class_id) if m.person_id == person_id),
            None,
        )
        if member is None:
            raise ClassNotFound("Esa persona no es parte de esta clase.")
        return build_student_detail(person_id, member.alias, await self._activity.read(class_id))
