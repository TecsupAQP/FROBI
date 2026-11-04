"""M10 · Herramientas recomendadas.

Stub: returns example data from a fixed catalogue. The real use cases replace each body.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from frobi.shared.presentation import AUTH_RESPONSES, require_token

from .schemas import RecommendationOut, RecommendationRequest, ToolOut

router = APIRouter(
    prefix="/tools",
    tags=["M10 · Herramientas"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

CATALOGUE = [
    ToolOut(
        id="google-scholar",
        name="Google Académico",
        need="verify_source",
        use_for="Buscar artículos que respalden un dato.",
        avoid_for="Resumir tu propio material.",
    ),
    ToolOut(
        id="notebooklm",
        name="NotebookLM",
        need="study_material",
        use_for="Preguntar sobre tus propios documentos.",
        avoid_for="Buscar información que no está en tus documentos.",
    ),
    ToolOut(
        id="wolfram-alpha",
        name="Wolfram Alpha",
        need="calculate",
        use_for="Verificar cálculos y unidades.",
        avoid_for="Explicaciones largas en palabras.",
    ),
    ToolOut(
        id="languagetool",
        name="LanguageTool",
        need="write",
        use_for="Revisar ortografía y gramática de tu borrador.",
        avoid_for="Decidir si una afirmación es cierta.",
    ),
    ToolOut(
        id="excalidraw",
        name="Excalidraw",
        need="visualize",
        use_for="Dibujar un esquema propio del tema.",
        avoid_for="Generar contenido automático.",
    ),
]


@router.post("/recommendations", summary="Recomendar una herramienta para una necesidad")
async def recommend_tool(body: RecommendationRequest) -> RecommendationOut:
    tool = next((t for t in CATALOGUE if t.need == body.need), CATALOGUE[0])
    return RecommendationOut(
        tool=tool,
        why=f"Sirve para: {tool.use_for[0].lower()}{tool.use_for[1:]}",
        when_not=f"No la uses para: {tool.avoid_for[0].lower()}{tool.avoid_for[1:]}",
    )


@router.get("", summary="Catálogo fijo de herramientas, filtrable por necesidad")
async def list_tools(
    need: Annotated[str | None, Query(max_length=60)] = None,
) -> list[ToolOut]:
    return [tool for tool in CATALOGUE if need is None or tool.need == need]
