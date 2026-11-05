"""M3 · Material."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from frobi.modules.materials.application import (
    CreateMaterialCommand,
    CreateMaterialHandler,
    CreateWorkCommand,
    CreateWorkHandler,
    GetMaterialHandler,
    ListSamplesHandler,
    UploadMaterialCommand,
    UploadMaterialHandler,
)
from frobi.modules.materials.domain import MAX_UPLOAD_BYTES, FileTooLarge, MaterialKind
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentPersonId,
    problem,
)

from .dependencies import (
    get_create_material,
    get_create_work,
    get_get_material,
    get_list_samples,
    get_upload_material,
)
from .schemas import (
    CreateMaterialRequest,
    CreateWorkRequest,
    MaterialOut,
    MaterialSummaryOut,
    WorkOut,
)

router = APIRouter(tags=["M3 · Material"], responses=AUTH_RESPONSES)


@router.get("/materials/samples", summary="Guías de ejemplo")
async def list_samples(
    _: CurrentPersonId,
    handler: Annotated[ListSamplesHandler, Depends(get_list_samples)],
) -> list[MaterialSummaryOut]:
    return [MaterialSummaryOut.from_domain(m) for m in await handler.handle()]


@router.post(
    "/materials",
    status_code=status.HTTP_201_CREATED,
    summary="Crear un material pegando texto",
    responses={422: problem("Título o texto vacío (`Materials.InvalidTitle`, `EmptyText`).")},
)
async def create_material(
    body: CreateMaterialRequest,
    person_id: CurrentPersonId,
    handler: Annotated[CreateMaterialHandler, Depends(get_create_material)],
) -> MaterialOut:
    material = await handler.handle(
        CreateMaterialCommand(
            owner_id=person_id, title=body.title, kind=MaterialKind(body.kind), text=body.text
        )
    )
    return MaterialOut.from_domain(material)


@router.post(
    "/materials/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Subir un PDF (máximo 10 MB) y obtener su texto",
    responses={
        422: problem(
            "PDF ilegible o sin texto (`Materials.PdfUnreadable`) "
            "o más de 10 MB (`Materials.FileTooLarge`)."
        ),
    },
)
async def upload_material(
    person_id: CurrentPersonId,
    handler: Annotated[UploadMaterialHandler, Depends(get_upload_material)],
    file: Annotated[UploadFile, File(description="PDF de hasta 10 MB.")],
    title: Annotated[str, Form(min_length=1, max_length=120)],
    kind: Annotated[Literal["guide", "brief", "draft"], Form()] = "guide",
) -> MaterialOut:
    # Read one byte past the limit so a huge upload is rejected without loading it all.
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise FileTooLarge()
    material = await handler.handle(
        UploadMaterialCommand(owner_id=person_id, title=title, kind=MaterialKind(kind), data=data)
    )
    return MaterialOut.from_domain(material)


@router.get(
    "/materials/{material_id}",
    summary="Detalle de un material y su texto",
    responses=NOT_FOUND_RESPONSES,
)
async def get_material(
    material_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GetMaterialHandler, Depends(get_get_material)],
) -> MaterialOut:
    return MaterialOut.from_domain(await handler.handle(person_id, material_id))


@router.post(
    "/works",
    status_code=status.HTTP_201_CREATED,
    summary="Organizar consigna y borrador (sin juzgar la autoría)",
    responses={
        **NOT_FOUND_RESPONSES,
        422: problem("La consigna no es `brief` o el borrador no es `draft`."),
    },
)
async def create_work(
    body: CreateWorkRequest,
    person_id: CurrentPersonId,
    handler: Annotated[CreateWorkHandler, Depends(get_create_work)],
) -> WorkOut:
    work = await handler.handle(
        CreateWorkCommand(
            person_id=person_id,
            brief_material_id=body.brief_material_id,
            draft_material_id=body.draft_material_id,
        )
    )
    return WorkOut.from_domain(work)
