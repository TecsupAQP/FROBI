"""Fixed catalogue of 5 tools (RF22) and how to pick one for a need or a reviewed claim (RF21).

Fixed and versioned here on purpose: nobody edits it at runtime, so it needs no table.
"""

from dataclasses import dataclass
from enum import StrEnum

from .errors import NeedRequired


class Need(StrEnum):
    VERIFY_SOURCE = "verify_source"
    STUDY_MATERIAL = "study_material"
    CALCULATE = "calculate"
    WRITE = "write"
    VISUALIZE = "visualize"


@dataclass(frozen=True, slots=True)
class Tool:
    id: str
    name: str
    need: Need
    use_for: str
    avoid_for: str


CATALOGUE: tuple[Tool, ...] = (
    Tool(
        "google-scholar",
        "Google Académico",
        Need.VERIFY_SOURCE,
        "Buscar artículos que respalden un dato.",
        "Resumir tu propio material.",
    ),
    Tool(
        "notebooklm",
        "NotebookLM",
        Need.STUDY_MATERIAL,
        "Preguntar sobre tus propios documentos.",
        "Buscar información que no está en tus documentos.",
    ),
    Tool(
        "wolfram-alpha",
        "Wolfram Alpha",
        Need.CALCULATE,
        "Verificar cálculos y unidades.",
        "Explicaciones largas en palabras.",
    ),
    Tool(
        "languagetool",
        "LanguageTool",
        Need.WRITE,
        "Revisar ortografía y gramática de tu borrador.",
        "Decidir si una afirmación es cierta.",
    ),
    Tool(
        "excalidraw",
        "Excalidraw",
        Need.VISUALIZE,
        "Dibujar un esquema propio del tema.",
        "Generar contenido automático.",
    ),
)
_BY_NEED = {tool.need: tool for tool in CATALOGUE}

# What a reviewed claim (M9) asks for next.
NEED_FOR_CLAIM_STATUS: dict[str, Need] = {
    "unverifiable": Need.VERIFY_SOURCE,
    "contradicts": Need.STUDY_MATERIAL,
    "supported": Need.WRITE,
}


def tools_for(need: Need | None) -> list[Tool]:
    return [tool for tool in CATALOGUE if need is None or tool.need is need]


def _lower_first(sentence: str) -> str:
    return sentence[:1].lower() + sentence[1:]


@dataclass(frozen=True, slots=True)
class Recommendation:
    tool: Tool
    why: str
    when_not: str


def recommend(need: Need | None, claim: tuple[str, str] | None = None) -> Recommendation:
    """``claim`` is (fragment, status) of a reviewed claim; it decides the need when given."""
    if claim is not None:
        fragment, status = claim
        need = NEED_FOR_CLAIM_STATUS[status]
    if need is None:
        raise NeedRequired()
    tool = _BY_NEED[need]
    when_not = f"No la uses para: {_lower_first(tool.avoid_for)}"
    if claim is None:
        return Recommendation(tool, f"Sirve para: {_lower_first(tool.use_for)}", when_not)
    fragment, status = claim
    fragment = fragment.strip().rstrip(".")
    why = {
        "unverifiable": f"Tu material no respalda «{fragment}». Busca ahí una fuente que lo "
        "confirme o lo descarte.",
        "contradicts": f"Tu material dice otra cosa sobre «{fragment}». Vuelve a tus "
        "documentos y pregúntales qué dicen exactamente.",
        "supported": f"Tu material respalda «{fragment}». Ahora revisa cómo lo escribiste.",
    }[status]
    return Recommendation(tool, why, when_not)
