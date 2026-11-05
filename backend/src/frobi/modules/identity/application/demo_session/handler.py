"""Enter as one of the demo people (docente demo, Ana, Luis) to present FROBI.

Every normal entry creates a new person, so without this nobody could open the seeded demo
class from the front. It only exists while the server runs as ``local`` or ``demo``.
"""

from frobi.modules.identity.application.ports import (
    ClassMembership,
    DemoDirectory,
    PersonRepository,
    SessionStore,
)
from frobi.modules.identity.application.start_session import StartSessionResult
from frobi.modules.identity.domain import DemoNotSeeded, DemoUnavailable


class DemoSessionHandler:
    def __init__(
        self,
        persons: PersonRepository,
        sessions: SessionStore,
        memberships: ClassMembership,
        demo: DemoDirectory,
        *,
        enabled: bool,
    ) -> None:
        self._persons = persons
        self._sessions = sessions
        self._memberships = memberships
        self._demo = demo
        self._enabled = enabled

    async def handle(self, who: str) -> StartSessionResult:
        if not self._enabled:
            raise DemoUnavailable()
        person_id = await self._demo.person_for(who)
        person = None if person_id is None else await self._persons.get(person_id)
        if person is None:
            raise DemoNotSeeded()
        token = await self._sessions.create(person.id)
        membership = await self._memberships.active_for(person.id)
        return StartSessionResult(token=token, person=person, membership=membership)
