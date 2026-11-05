"""ClaimLookup over the public API of claim_review."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import claim_review
from frobi.modules.tools.application.ports import ReviewedClaim


class ClaimLookupAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._claims = claim_review.get_claim_handler(session)

    async def find(self, person_id: UUID, claim_id: UUID) -> ReviewedClaim | None:
        claim = await self._claims.find(person_id, claim_id)
        return None if claim is None else ReviewedClaim(claim.fragment, claim.status.value)
