"""M4 y M5 · Adaptación, receta y límites.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.shared.presentation import AUTH_RESPONSES, NOT_FOUND_RESPONSES, require_token

from .schemas import (
    AdaptationContent,
    AdaptationOut,
    ContentSection,
    CreateAdaptationRequest,
    Format,
    FormatOut,
    Recipe,
)

router = APIRouter(
    tags=["M4 y M5 · Adaptación"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

EXAMPLE_ADAPTATION_ID = UUID("00000000-0000-4000-8000-00000000d001")
EXAMPLE_MATERIAL_ID = UUID("00000000-0000-4000-8000-00000000a001")
CREATED_AT = datetime(2026, 11, 4, 12, 5, tzinfo=UTC)

FORMATS = [
    FormatOut(
        id=Format.VISUAL_MAP,
        name="Mapa visual",
        description="Las ideas y cómo se conectan.",
        icon="map",
        suggested=False,
    ),
    FormatOut(
        id=Format.REAL_EXAMPLE,
        name="Ejemplo real",
        description="El tema aplicado a un caso de la industria.",
        icon="factory",
        suggested=False,
    ),
    FormatOut(
        id=Format.EASY_READ,
        name="Lectura fácil",
        description="Frases cortas y palabras simples.",
        icon="text",
        suggested=True,
    ),
    FormatOut(
        id=Format.AUDIO,
        name="Audio",
        description="Te lo leemos en voz alta.",
        icon="volume",
        suggested=False,
    ),
]

AI_NOTICE = (
    "Esto lo generó una IA a partir de tu material. Puede equivocarse: compáralo con la guía."
)


def _adaptation(adaptation_id: UUID, material_id: UUID, fmt: Format) -> AdaptationOut:
    recipe = Recipe(
        context="Estudiante de Mecatrónica que lee la guía de sensores industriales.",
        goal="Entender qué hace un sensor y diferenciar inductivos de capacitivos.",
        level="Primer año, sin conocimientos previos.",
        format=fmt,
    )
    return AdaptationOut(
        id=adaptation_id,
        material_id=material_id,
        format=fmt,
        content=AdaptationContent(
            title="Sensores industriales",
            sections=[
                ContentSection(
                    heading="¿Qué es un sensor?",
                    body="Un sensor mide algo del mundo y lo convierte en una señal eléctrica.",
                ),
                ContentSection(
                    heading="Dos tipos",
                    body="Se diferencian por lo que pueden detectar.",
                    items=[
                        "Inductivo: detecta metales sin tocarlos.",
                        "Capacitivo: detecta también plásticos y líquidos.",
                    ],
                ),
            ],
            plain_text=(
                "Un sensor mide algo del mundo y lo convierte en una señal eléctrica. "
                "El inductivo detecta metales sin tocarlos. "
                "El capacitivo detecta también plásticos y líquidos."
            ),
        ),
        recipe=recipe,
        prompt_text=(
            f"Contexto: {recipe.context}\nObjetivo: {recipe.goal}\n"
            f"Nivel: {recipe.level}\nFormato: {fmt.value}\n"
            "Usa solo el material que te doy y avisa si algo no está en él."
        ),
        ai_notice=AI_NOTICE,
        fallback=False,
        created_at=CREATED_AT,
    )


@router.get("/formats", summary="Los 4 formatos y el sugerido según el perfil")
async def list_formats() -> list[FormatOut]:
    return FORMATS


@router.post(
    "/materials/{material_id}/adaptations",
    status_code=status.HTTP_201_CREATED,
    summary="Adaptar un material a un formato (tope de 15 s, con respaldo)",
    responses=NOT_FOUND_RESPONSES,
)
async def create_adaptation(material_id: UUID, body: CreateAdaptationRequest) -> AdaptationOut:
    return _adaptation(EXAMPLE_ADAPTATION_ID, material_id, body.format)


@router.get(
    "/adaptations/{adaptation_id}",
    summary="Volver a ver una adaptación",
    responses=NOT_FOUND_RESPONSES,
)
async def get_adaptation(adaptation_id: UUID) -> AdaptationOut:
    return _adaptation(adaptation_id, EXAMPLE_MATERIAL_ID, Format.EASY_READ)
