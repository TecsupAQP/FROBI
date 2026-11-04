"""M3 · Material.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from frobi.modules.materials.domain.errors import MAX_UPLOAD_BYTES, FileTooLarge, PdfUnreadable
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    problem,
    require_token,
)

from .schemas import (
    CreateMaterialRequest,
    CreateWorkRequest,
    MaterialKind,
    MaterialOut,
    MaterialSource,
    MaterialSummaryOut,
    OrganizedWork,
    WorkOut,
)

router = APIRouter(
    tags=["M3 · Material"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

SAMPLE_ID = UUID("00000000-0000-4000-8000-00000000a001")
EXAMPLE_WORK_ID = UUID("00000000-0000-4000-8000-00000000b001")
CREATED_AT = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)
SAMPLE_TEXT = (
    "Guía de sensores industriales.\n"
    "Un sensor convierte una magnitud física, como la temperatura o la presión, en una señal "
    "eléctrica. Los sensores inductivos detectan metales sin contacto. Los capacitivos detectan "
    "también plásticos y líquidos. Un termopar mide temperatura por la unión de dos metales."
)
SAMPLES = [
    MaterialSummaryOut(
        id=SAMPLE_ID,
        title="Guía de sensores industriales",
        kind=MaterialKind.GUIDE,
        source=MaterialSource.SAMPLE,
        preview=SAMPLE_TEXT[:120],
    )
]


def _material(
    material_id: UUID, title: str, kind: MaterialKind, source: MaterialSource, text: str
) -> MaterialOut:
    return MaterialOut(
        id=material_id,
        title=title,
        kind=kind,
        source=source,
        class_id=None,
        extracted_text=text,
        created_at=CREATED_AT,
    )


@router.get("/materials/samples", summary="Guías de ejemplo")
async def list_samples() -> list[MaterialSummaryOut]:
    return SAMPLES


@router.post(
    "/materials",
    status_code=status.HTTP_201_CREATED,
    summary="Crear un material pegando texto",
)
async def create_material(body: CreateMaterialRequest) -> MaterialOut:
    return _material(
        UUID("00000000-0000-4000-8000-00000000a002"),
        body.title,
        MaterialKind(body.kind),
        MaterialSource.PASTE,
        body.text,
    )


@router.post(
    "/materials/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Subir un PDF (máximo 10 MB) y obtener su texto",
    responses={
        422: problem("PDF ilegible (`Materials.PdfUnreadable`) o más de 10 MB."),
    },
)
async def upload_material(
    file: Annotated[UploadFile, File(description="PDF de hasta 10 MB.")],
    title: Annotated[str, Form(min_length=1, max_length=120)],
    kind: Annotated[Literal["guide", "brief", "draft"], Form()] = "guide",
) -> MaterialOut:
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise FileTooLarge()
    if not content.startswith(b"%PDF"):
        raise PdfUnreadable()
    return _material(
        UUID("00000000-0000-4000-8000-00000000a003"),
        title,
        MaterialKind(kind),
        MaterialSource.UPLOAD,
        SAMPLE_TEXT,
    )


@router.get(
    "/materials/{material_id}",
    summary="Detalle de un material y su texto",
    responses=NOT_FOUND_RESPONSES,
)
async def get_material(material_id: UUID) -> MaterialOut:
    return _material(
        material_id,
        "Guía de sensores industriales",
        MaterialKind.GUIDE,
        MaterialSource.SAMPLE,
        SAMPLE_TEXT,
    )


@router.post(
    "/works",
    status_code=status.HTTP_201_CREATED,
    summary="Organizar consigna y borrador (sin juzgar la autoría)",
    responses=NOT_FOUND_RESPONSES,
)
async def create_work(body: CreateWorkRequest) -> WorkOut:
    return WorkOut(
        id=EXAMPLE_WORK_ID,
        brief_material_id=body.brief_material_id,
        draft_material_id=body.draft_material_id,
        organized=OrganizedWork(
            requirements=[
                "Explicar qué es un sensor",
                "Comparar dos tipos de sensores",
                "Dar un ejemplo industrial",
            ],
            topics=["Sensores inductivos", "Sensores capacitivos"],
            missing=["Dar un ejemplo industrial"],
        ),
    )
