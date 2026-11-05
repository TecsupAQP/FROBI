from typing import Protocol
from uuid import UUID


class TokenResolver(Protocol):
    """Maps a bearer token to the person it belongs to. Identity implements it on Redis."""

    async def resolve(self, token: str) -> UUID | None: ...
