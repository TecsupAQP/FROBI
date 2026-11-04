"""GET /health: is the API up, and can it reach Postgres and Redis? No auth."""

from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated, Literal, cast

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from frobi.shared.application import HealthProbe, check_health

router = APIRouter(tags=["health"])


class ComponentStatus(StrEnum):
    UP = "up"
    DOWN = "down"


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, ComponentStatus]


def get_health_probes(request: Request) -> Sequence[HealthProbe]:
    return cast(Sequence[HealthProbe], request.app.state.health_probes)


def get_health_timeout(request: Request) -> float:
    return cast(float, request.app.state.settings.health_timeout_seconds)


@router.get(
    "/health",
    summary="Estado de la API, Postgres y Redis",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "Alguna dependencia no responde."}},
)
async def health(
    response: Response,
    probes: Annotated[Sequence[HealthProbe], Depends(get_health_probes)],
    timeout_seconds: Annotated[float, Depends(get_health_timeout)],
) -> HealthResponse:
    results = await check_health(probes, timeout_seconds)
    healthy = all(results.values())
    if not healthy:
        response.status_code = 503
    return HealthResponse(
        status="ok" if healthy else "degraded",
        checks={
            name: ComponentStatus.UP if ok else ComponentStatus.DOWN for name, ok in results.items()
        },
    )
