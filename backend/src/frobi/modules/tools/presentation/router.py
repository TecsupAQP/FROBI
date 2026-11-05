"""M10 · Herramientas recomendadas."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from frobi.modules.tools.application import ListToolsHandler, RecommendToolHandler
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentPersonId,
    problem,
    require_token,
)

from .dependencies import get_recommend_tool
from .schemas import RecommendationOut, RecommendationRequest, ToolOut

router = APIRouter(
    prefix="/tools",
    tags=["M10 · Herramientas"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)


@router.post(
    "/recommendations",
    summary="Recomendar una herramienta para una necesidad o una afirmación",
    responses={
        **NOT_FOUND_RESPONSES,
        422: problem(
            "Falta `need` o `claim_id` (`Tools.NeedRequired`) o la necesidad no existe "
            "(`Tools.UnknownNeed`)."
        ),
    },
)
async def recommend_tool(
    body: RecommendationRequest,
    person_id: CurrentPersonId,
    handler: Annotated[RecommendToolHandler, Depends(get_recommend_tool)],
) -> RecommendationOut:
    return RecommendationOut.from_domain(await handler.handle(person_id, body.need, body.claim_id))


@router.get(
    "",
    summary="Catálogo fijo de herramientas, filtrable por necesidad",
    responses={422: problem("La necesidad no existe (`Tools.UnknownNeed`).")},
)
async def list_tools(
    need: Annotated[str | None, Query(max_length=60)] = None,
) -> list[ToolOut]:
    return [ToolOut.from_domain(tool) for tool in await ListToolsHandler().handle(need)]
