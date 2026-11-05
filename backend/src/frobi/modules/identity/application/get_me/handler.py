"""Who is the current person, which class they are in, and whether the wizard is done (RF32)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.identity.application.ports import (
    ActiveMembership,
    ClassMembership,
    OnboardingStatus,
    OnboardingStatusReader,
    PersonRepository,
)
from frobi.modules.identity.domain import Person
from frobi.shared.application import Unauthenticated


@dataclass(frozen=True, slots=True)
class MeView:
    person: Person
    membership: ActiveMembership | None
    onboarding: OnboardingStatus


class GetMeHandler:
    def __init__(
        self,
        persons: PersonRepository,
        memberships: ClassMembership,
        onboarding: OnboardingStatusReader,
    ) -> None:
        self._persons = persons
        self._memberships = memberships
        self._onboarding = onboarding

    async def handle(self, person_id: UUID) -> MeView:
        person = await self._persons.get(person_id)
        if person is None:
            # A valid token whose person no longer exists is treated as no session at all.
            raise Unauthenticated()
        return MeView(
            person=person,
            membership=await self._memberships.active_for(person_id),
            onboarding=await self._onboarding.for_person(person_id),
        )
