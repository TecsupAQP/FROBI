"""ClassContext (shared port) over the placeholder membership until classrooms (M12) exists."""

from uuid import UUID

from redis.asyncio import Redis

from .placeholder_adapters import ExampleClassMembership


class ExampleClassContext:
    def __init__(self, redis: "Redis") -> None:
        self._memberships = ExampleClassMembership(redis)

    async def active_class(self, person_id: UUID) -> UUID | None:
        membership = await self._memberships.active_for(person_id)
        return None if membership is None else membership.class_id
