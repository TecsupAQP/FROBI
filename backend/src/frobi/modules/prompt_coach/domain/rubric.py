"""Deterministic rubric for the 4 pieces of a prompt (context, goal, level, format), 0 to 4 each.

It looks for concrete signals in Spanish (accent-insensitive). It is the scorer when no AI
provider answers, and the reference that keeps AI scores honest in tests.
"""

import re
from dataclasses import dataclass
from enum import StrEnum

from frobi.shared.domain import text


class RecipePiece(StrEnum):
    CONTEXT = "context"
    GOAL = "goal"
    LEVEL = "level"
    FORMAT = "format"


PIECE_NAMES: dict[RecipePiece, str] = {
    RecipePiece.CONTEXT: "contexto",
    RecipePiece.GOAL: "objetivo",
    RecipePiece.LEVEL: "nivel",
    RecipePiece.FORMAT: "formato",
}

TIPS: dict[RecipePiece, str] = {
    RecipePiece.CONTEXT: "Cuenta quién eres y de qué material hablas: «Soy estudiante de … y "
    "estoy leyendo …».",
    RecipePiece.GOAL: "Di qué quieres lograr: «Explícame … para poder …».",
    RecipePiece.LEVEL: "Cuenta tu nivel: por ejemplo, «soy de primer año» o «explícalo con "
    "palabras simples».",
    RecipePiece.FORMAT: "Pide un formato: «en una tabla», «en 3 puntos» o «paso a paso».",
}


@dataclass(frozen=True, slots=True)
class Signals:
    strong: tuple[str, ...]  # each one found is worth 2 points
    weak: tuple[str, ...] = ()  # each one found is worth 1 point


# Phrases are matched on folded text («Explícame» → «explicame») with word boundaries.
SIGNALS: dict[RecipePiece, Signals] = {
    RecipePiece.CONTEXT: Signals(
        strong=("soy", "estudio", "estudiante", "estoy leyendo", "mi carrera", "mi curso",
                "segun la guia", "segun el material", "segun mi material", "de mi clase"),
        weak=("guia", "material", "apuntes", "texto", "documento", "clase", "curso", "carrera",
              "tema", "semestre", "profesor", "docente"),
    ),
    RecipePiece.GOAL: Signals(
        strong=("explicame", "explica", "resume", "resumeme", "compara", "dame", "ayudame",
                "quiero entender", "quiero aprender", "necesito", "ensename", "describe",
                "dime", "hazme"),
        weak=("para poder", "para entender", "para preparar", "para estudiar", "porque",
              "diferencia", "ejemplo", "practicar", "repasar", "examen"),
    ),
    RecipePiece.LEVEL: Signals(
        strong=("primer ano", "segundo ano", "principiante", "sin conocimientos", "no se nada",
                "palabras simples", "como si tuviera", "nivel basico", "nivel avanzado",
                "ya se", "con detalle"),
        weak=("basico", "sencillo", "simple", "facil", "nivel", "avanzado", "tecnico",
              "detallado", "despacio"),
    ),
    RecipePiece.FORMAT: Signals(
        strong=("tabla", "en puntos", "lista", "paso a paso", "esquema", "mapa", "vinetas",
                "en una frase", "resumen corto", "preguntas"),
        weak=("breve", "corto", "maximo", "ejemplo", "parrafo", "pasos", "puntos", "columnas",
              "palabras"),
    ),
}  # fmt: skip

_NUMBER_WITH_UNIT = re.compile(r"\b\d+\s+(puntos|pasos|ideas|frases|lineas|palabras|ejemplos)\b")


def _found(phrase: str, folded: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", folded) is not None


def _score(piece: RecipePiece, folded: str) -> int:
    signals = SIGNALS[piece]
    points = 2 * sum(_found(p, folded) for p in signals.strong)
    points += sum(_found(p, folded) for p in signals.weak)
    if piece is RecipePiece.FORMAT and _NUMBER_WITH_UNIT.search(folded):
        points += 2
    return min(4, points)


FEEDBACK: dict[int, str] = {
    0: "Falta: no aparece en tu instrucción.",
    1: "Apenas se insinúa.",
    2: "Está, pero puede ser más concreto.",
    3: "Bien planteado.",
    4: "Muy claro.",
}


def score_prompt(prompt: str) -> dict[RecipePiece, int]:
    folded = text.fold(prompt)
    return {piece: _score(piece, folded) for piece in RecipePiece}


def improve(prompt: str, scores: dict[RecipePiece, int], material_title: str | None) -> str:
    """Keep the person's words and add only the pieces that are weak (score below 3)."""
    about = f"«{material_title}»" if material_title else "mi material"
    base = " ".join(prompt.split()).rstrip(" .?!¿¡")
    parts: list[str] = []
    if scores[RecipePiece.CONTEXT] < 3:
        parts.append(f"Soy estudiante y estoy estudiando {about}.")
    parts.append(base[:1].upper() + base[1:] + ".")
    if scores[RecipePiece.GOAL] < 3:
        parts.append("Quiero entender las ideas principales para poder explicarlas.")
    if scores[RecipePiece.LEVEL] < 3:
        parts.append("Explícalo con palabras simples, sin conocimientos previos.")
    if scores[RecipePiece.FORMAT] < 3:
        parts.append("Respóndeme en 3 puntos cortos.")
    if material_title:
        parts.append("Usa solo el material que te doy.")
    return " ".join(parts)
