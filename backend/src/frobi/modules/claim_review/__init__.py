"""Public API of claim_review: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from .application import GetClaimHandler
from .domain import Claim, ClaimStatus


def get_claim_handler(session: AsyncSession) -> GetClaimHandler:
    """One claim of the person's own reviews; ``find`` returns None for anyone else."""
    from .infrastructure import SqlAlchemyClaimRepository

    return GetClaimHandler(SqlAlchemyClaimRepository(session))


__all__ = ["Claim", "ClaimStatus", "GetClaimHandler", "get_claim_handler"]
