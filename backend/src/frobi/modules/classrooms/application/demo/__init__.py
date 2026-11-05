"""Who the demo people are, for the demo sign-in (identity). Only the seeded demo class."""

from uuid import UUID

from frobi.modules.classrooms.application.ports import MembershipRepository
from frobi.modules.classrooms.domain import (
    DEMO_CLASS_ID,
    DEMO_STUDENTS,
    DEMO_TEACHER_ID,
    MembershipStatus,
)

DEMO_PEOPLE = ("teacher", *DEMO_STUDENTS)


class DemoPeopleHandler:
    def __init__(self, memberships: MembershipRepository) -> None:
        self._memberships = memberships

    async def person_for(self, who: str) -> UUID | None:
        """``teacher``, ``ana`` or ``luis``. None when that student has not been seeded."""
        if who == "teacher":
            return DEMO_TEACHER_ID
        alias = DEMO_STUDENTS.get(who)
        if alias is None:
            return None
        members = await self._memberships.for_class(DEMO_CLASS_ID)
        joined = [
            m.person_id
            for m in members
            if m.alias == alias and m.status is MembershipStatus.JOINED and m.person_id
        ]
        return joined[-1] if joined else None


__all__ = ["DEMO_PEOPLE", "DemoPeopleHandler"]
