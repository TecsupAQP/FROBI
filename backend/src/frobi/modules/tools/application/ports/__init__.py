from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ReviewedClaim:
    fragment: str
    status: str


class ClaimLookup(Protocol):
    """Over the public API of claim_review: only the person's own claims."""

    async def find(self, person_id: UUID, claim_id: UUID) -> ReviewedClaim | None: ...


__all__ = ["ClaimLookup", "ReviewedClaim"]
