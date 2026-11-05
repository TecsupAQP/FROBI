"""Recommend a tool for a need or a reviewed claim (RF21); list the fixed catalogue (RF22)."""

from uuid import UUID

from frobi.modules.tools.application.ports import ClaimLookup
from frobi.modules.tools.domain import (
    ClaimNotAvailable,
    Need,
    Recommendation,
    Tool,
    UnknownNeed,
    recommend,
    tools_for,
)


def parse_need(raw: str | None) -> Need | None:
    if raw is None or not raw.strip():
        return None
    try:
        return Need(raw.strip().lower())
    except ValueError as error:
        raise UnknownNeed() from error


class RecommendToolHandler:
    def __init__(self, claims: ClaimLookup) -> None:
        self._claims = claims

    async def handle(
        self, person_id: UUID, need: str | None, claim_id: UUID | None
    ) -> Recommendation:
        parsed = parse_need(need)
        if claim_id is None:
            return recommend(parsed)
        claim = await self._claims.find(person_id, claim_id)
        if claim is None:
            raise ClaimNotAvailable()
        return recommend(parsed, (claim.fragment, claim.status))


class ListToolsHandler:
    async def handle(self, need: str | None) -> list[Tool]:
        return tools_for(parse_need(need))
