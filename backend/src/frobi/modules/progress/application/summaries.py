"""The person's own progress (RF15, RF16, RF42) and the closing summary (RF27), in words."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from frobi.modules.progress.application.ports import (
    PersonActivity,
    PersonActivityReader,
    RecipeView,
)

FORMAT_NAMES = {
    "visual_map": "mapa visual",
    "real_example": "ejemplo real",
    "easy_read": "lectura fácil",
    "audio": "audio",
}
MIN_ANSWERS_TO_RANK_A_FORMAT = 2
EMPTY_MESSAGE = (
    "Todavía no hay actividad. Adapta un material o responde unas preguntas y aquí verás cómo vas."
)


@dataclass(frozen=True, slots=True)
class FormatAccuracy:
    format: str
    correct: int
    total: int


@dataclass(frozen=True, slots=True)
class Progress:
    has_data: bool
    formats_used: list[tuple[str, int]]
    accuracy_by_format: list[FormatAccuracy]
    prompt_scores: list[tuple[datetime, int]]
    solved_without_ai: int
    message: str


def _accuracy(activity: PersonActivity) -> list[FormatAccuracy]:
    by_format: dict[str, list[bool]] = {}
    for answer in activity.answers:
        by_format.setdefault(answer.format, []).append(answer.is_correct)
    return [
        FormatAccuracy(fmt, sum(results), len(results))
        for fmt, results in sorted(by_format.items())
    ]


def _message(activity: PersonActivity, accuracy: list[FormatAccuracy], solved: int) -> str:
    parts: list[str] = []
    ranked = [a for a in accuracy if a.total >= MIN_ANSWERS_TO_RANK_A_FORMAT]
    if ranked:
        best = max(ranked, key=lambda a: (a.correct / a.total, a.total))
        parts.append(f"Aciertas más con {FORMAT_NAMES.get(best.format, best.format)}")
    elif accuracy:
        right, total = sum(a.correct for a in accuracy), sum(a.total for a in accuracy)
        parts.append(f"llevas {right} de {total} {'acierto' if total == 1 else 'aciertos'}")
    scores = [s.total for s in activity.prompt_scores]
    if len(scores) >= 2 and scores[-1] > scores[0]:
        parts.append(f"tus instrucciones mejoraron de {scores[0]} a {scores[-1]} de 16")
    elif scores:
        parts.append(f"tu última instrucción sacó {scores[-1]} de 16")
    if solved:
        parts.append(f"resolviste {solved} {'tarea' if solved == 1 else 'tareas'} sin IA")
    if not parts:
        return "Vas empezando: sigue probando formatos y preguntas."
    sentence = ", ".join(parts[:-1]) + (" y " if len(parts) > 1 else "") + parts[-1]
    return sentence[0].upper() + sentence[1:] + "."


def progress_of(activity: PersonActivity) -> Progress:
    if activity.empty:
        return Progress(False, [], [], [], 0, EMPTY_MESSAGE)
    accuracy = _accuracy(activity)
    solved = sum(h.solved_without_ai for h in activity.help)
    return Progress(
        has_data=True,
        formats_used=Counter(f.format for f in activity.formats).most_common(),
        accuracy_by_format=accuracy,
        prompt_scores=[(s.created_at, s.total) for s in activity.prompt_scores],
        solved_without_ai=solved,
        message=_message(activity, accuracy, solved),
    )


@dataclass(frozen=True, slots=True)
class JourneySummary:
    favorite_format: str | None
    learned_recipe: RecipeView | None
    best_prompt_score: int | None
    autonomy_level: int | None
    message: str


def journey_of(activity: PersonActivity) -> JourneySummary:
    formats = Counter(f.format for f in activity.formats)
    scores = activity.prompt_scores
    autonomy = scores[-1].autonomy_level if scores else None
    if activity.empty:
        message = EMPTY_MESSAGE
    elif autonomy == 3:
        message = "Ya sabes pedirle a la IA lo que necesitas y comprobarlo con tu material."
    elif autonomy == 2:
        message = "Ya pides con contexto. Suma tu nivel y el formato para armar la receta completa."
    else:
        message = "Buen comienzo. Prueba la receta de 4 piezas en tu próxima instrucción."
    return JourneySummary(
        favorite_format=formats.most_common(1)[0][0] if formats else None,
        learned_recipe=activity.latest_recipe,
        best_prompt_score=max((s.total for s in scores), default=None),
        autonomy_level=autonomy,
        message=message,
    )


class GetProgressHandler:
    def __init__(self, activity: PersonActivityReader) -> None:
        self._activity = activity

    async def handle(self, person_id: UUID) -> Progress:
        return progress_of(await self._activity.read(person_id))


class GetJourneySummaryHandler:
    def __init__(self, activity: PersonActivityReader) -> None:
        self._activity = activity

    async def handle(self, person_id: UUID) -> JourneySummary:
        return journey_of(await self._activity.read(person_id))
