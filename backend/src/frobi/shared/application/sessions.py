from typing import Protocol
from uuid import UUID


class TokenResolver(Protocol):
    """Maps a bearer token to the person it belongs to. Identity implements it on Redis."""

    async def resolve(self, token: str) -> UUID | None: ...


class ClassContext(Protocol):
    """The class a person is active in right now, or None (RNF16).

    Every activity row stores this ``class_id`` so the teacher panel can only ever see what was
    done inside the class.
    """

    async def active_class(self, person_id: UUID) -> UUID | None: ...
