"""M4 y M5 · Adaptación, receta y límites."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.modules.adaptations.application import (
    CreateAdaptationCommand,
    CreateAdaptationHandler,
    GetAdaptationHandler,
    ListFormatsHandler,
)
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentClassId,
    CurrentPersonId,
)

from .dependencies import get_create_adaptation, get_get_adaptation, get_list_formats
from .schemas import AdaptationOut, CreateAdaptationRequest, FormatOut

router = APIRouter(tags=["M4 y M5 · Adaptación"], responses=AUTH_RESPONSES)


@router.get("/formats", summary="Los 4 formatos y el sugerido según el perfil")
async def list_formats(
    person_id: CurrentPersonId,
    handler: Annotated[ListFormatsHandler, Depends(get_list_formats)],
) -> list[FormatOut]:
    return [FormatOut.from_option(option) for option in await handler.handle(person_id)]


@router.post(
    "/materials/{material_id}/adaptations",
    status_code=status.HTTP_201_CREATED,
    summary="Adaptar un material a un formato (tope de 15 s, con respaldo)",
    responses=NOT_FOUND_RESPONSES,
)
async def create_adaptation(
    material_id: UUID,
    body: CreateAdaptationRequest,
    person_id: CurrentPersonId,
    class_id: CurrentClassId,
    handler: Annotated[CreateAdaptationHandler, Depends(get_create_adaptation)],
) -> AdaptationOut:
    adaptation = await handler.handle(
        CreateAdaptationCommand(
            person_id=person_id, class_id=class_id, material_id=material_id, format=body.format
        )
    )
    return AdaptationOut.from_domain(adaptation)


@router.get(
    "/adaptations/{adaptation_id}",
    summary="Volver a ver una adaptación",
    responses=NOT_FOUND_RESPONSES,
)
async def get_adaptation(
    adaptation_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GetAdaptationHandler, Depends(get_get_adaptation)],
) -> AdaptationOut:
    return AdaptationOut.from_domain(await handler.handle(person_id, adaptation_id))
