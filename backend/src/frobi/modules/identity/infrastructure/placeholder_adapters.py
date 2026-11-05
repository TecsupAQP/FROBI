"""Temporary adapters for ports whose owning module is not built yet.

- ``ExampleClassMembership`` stands in for classrooms (M12, phase 2): one example class whose
  code is ``SENSOR1``. Joins are kept in Redis so ``/me`` reflects them. Replace it with an
  adapter over the classrooms public API when M12 lands.
- ``PendingOnboardingStatus`` stands in for onboarding/settings (M2): nobody has finished the
  wizard yet.
"""

from datetime import timedelta
from uuid import UUID

from redis.asyncio import Redis

from frobi.modules.identity.application.ports import ActiveMembership, ClassRef, OnboardingStatus

EXAMPLE_CLASS = ClassRef(id=UUID("00000000-0000-4000-8000-0000000000c1"), name="Sensores 2026-II")
EXAMPLE_CODE = "SENSOR1"
MEMBERSHIP_TTL = timedelta(days=30)


class ExampleClassMembership:
    def __init__(self, redis: "Redis") -> None:
        self._redis = redis

    @staticmethod
    def _key(person_id: UUID) -> str:
        return f"placeholder:membership:{person_id}"

    async def find_by_code(self, code: str) -> ClassRef | None:
        return EXAMPLE_CLASS if code.strip().upper() == EXAMPLE_CODE else None

    async def join(self, person_id: UUID, class_ref: ClassRef) -> ActiveMembership:
        await self._redis.set(self._key(person_id), str(class_ref.id), ex=MEMBERSHIP_TTL)
        return ActiveMembership(class_id=class_ref.id, class_name=class_ref.name)

    async def active_for(self, person_id: UUID) -> ActiveMembership | None:
        value = await self._redis.get(self._key(person_id))
        if value != str(EXAMPLE_CLASS.id):
            return None
        return ActiveMembership(class_id=EXAMPLE_CLASS.id, class_name=EXAMPLE_CLASS.name)


class PendingOnboardingStatus:
    async def for_person(self, person_id: UUID) -> OnboardingStatus:
        return OnboardingStatus(done=False, intro_status="pending")
