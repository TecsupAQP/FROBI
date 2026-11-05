from uuid import UUID, uuid4

import pytest

from frobi.modules.tools.application import ListToolsHandler, RecommendToolHandler
from frobi.modules.tools.application.ports import ReviewedClaim
from frobi.modules.tools.domain import (
    CATALOGUE,
    ClaimNotAvailable,
    Need,
    NeedRequired,
    UnknownNeed,
)

ANA = uuid4()
CLAIM_ID = uuid4()


class Claims:
    def __init__(self, status: str) -> None:
        self._claim = ReviewedClaim("Los ópticos son los más baratos.", status)

    async def find(self, person_id: UUID, claim_id: UUID) -> ReviewedClaim | None:
        return self._claim if person_id == ANA and claim_id == CLAIM_ID else None


def test_the_catalogue_has_5_tools_one_per_need() -> None:
    assert len(CATALOGUE) == 5
    assert {tool.need for tool in CATALOGUE} == set(Need)
    assert all(tool.use_for and tool.avoid_for for tool in CATALOGUE)


async def test_filter_by_need() -> None:
    assert [t.id for t in await ListToolsHandler().handle("calculate")] == ["wolfram-alpha"]
    assert len(await ListToolsHandler().handle(None)) == 5


async def test_an_unknown_need_is_a_clear_error() -> None:
    with pytest.raises(UnknownNeed):
        await ListToolsHandler().handle("magia")


async def test_recommend_for_a_need() -> None:
    recommendation = await RecommendToolHandler(Claims("supported")).handle(
        ANA, " VERIFY_SOURCE ", None
    )

    assert recommendation.tool.id == "google-scholar"
    assert recommendation.why == "Sirve para: buscar artículos que respalden un dato."
    assert recommendation.when_not == "No la uses para: resumir tu propio material."


@pytest.mark.parametrize(
    ("status", "tool", "says"),
    [
        ("unverifiable", "google-scholar", "Tu material no respalda"),
        ("contradicts", "notebooklm", "Tu material dice otra cosa"),
        ("supported", "languagetool", "Tu material respalda"),
    ],
)
async def test_a_reviewed_claim_decides_the_tool(status: str, tool: str, says: str) -> None:
    recommendation = await RecommendToolHandler(Claims(status)).handle(ANA, None, CLAIM_ID)

    assert recommendation.tool.id == tool
    assert recommendation.why.startswith(says)
    assert "«Los ópticos son los más baratos»" in recommendation.why


async def test_someone_elses_claim_is_not_found() -> None:
    with pytest.raises(ClaimNotAvailable):
        await RecommendToolHandler(Claims("unverifiable")).handle(uuid4(), None, CLAIM_ID)


async def test_without_need_or_claim_there_is_nothing_to_recommend() -> None:
    with pytest.raises(NeedRequired):
        await RecommendToolHandler(Claims("supported")).handle(ANA, None, None)
