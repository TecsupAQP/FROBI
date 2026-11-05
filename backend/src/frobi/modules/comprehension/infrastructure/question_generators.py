"""Questions: the model first (15 s cap, validated), then prewritten ones for the sample guide or
«completa la frase» built from the person's own text."""

import json
from functools import cache
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.comprehension.application.ports import QuizContext
from frobi.modules.comprehension.domain import (
    InvalidQuestion,
    Option,
    QuestionDraft,
    QuestionKind,
    cloze_questions,
)
from frobi.shared.infrastructure.llm import (
    SYSTEM_PROMPT,
    LlmClient,
    RateLimiter,
    call_with_fallback,
)

FALLBACKS_DIR = Path(__file__).parent / "fallbacks"
MAX_MATERIAL_CHARS = 20_000


def _draft(data: dict[str, Any]) -> QuestionDraft:
    return QuestionDraft(
        statement=data["statement"],
        options=tuple(Option(str(i), str(t)) for i, t in data["options"]),
        correct_option=data["correct_option"],
        feedback_correct=data["feedback_correct"],
        feedback_wrong=data["feedback_wrong"],
    ).shuffled()


@cache
def _prewritten() -> dict[tuple[UUID, QuestionKind], tuple[QuestionDraft, ...]]:
    table: dict[tuple[UUID, QuestionKind], tuple[QuestionDraft, ...]] = {}
    for path in sorted(FALLBACKS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        material_id = UUID(data["material_id"])
        for kind in QuestionKind:
            table[(material_id, kind)] = tuple(_draft(q) for q in data[kind.value])
    return table


def _rotate(items: tuple[QuestionDraft, ...], n: int, skip: int) -> list[QuestionDraft]:
    start = skip % len(items)
    return [items[(start + i) % len(items)] for i in range(min(n, len(items)))]


class FallbackQuestionGenerator:
    async def generate(
        self,
        *,
        requested_by: UUID,
        context: QuizContext,
        kind: QuestionKind,
        n: int,
        skip: int = 0,
    ) -> list[QuestionDraft]:
        prewritten = _prewritten().get((context.material_id, kind))
        if prewritten:
            return _rotate(prewritten, n, skip)
        drafts = cloze_questions(context.material_text, n, skip=skip)
        if not drafts and skip:
            drafts = cloze_questions(context.material_text, n)  # wrap around
        return drafts


class _QuestionJson(BaseModel):
    statement: str = Field(min_length=5, max_length=500)
    options: list[str] = Field(min_length=3, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    feedback_correct: str = Field(min_length=1, max_length=500)
    feedback_wrong: str = Field(min_length=1, max_length=500)


class _QuizJson(BaseModel):
    questions: list[_QuestionJson] = Field(min_length=1, max_length=3)


KIND_RULES = {
    QuestionKind.COMPREHENSION: "preguntas de comprensión sobre ideas del material",
    QuestionKind.TRANSFER: "una pregunta de aplicación a un caso nuevo, que se pueda "
    "resolver con lo que dice el material",
}


class LlmQuestionGenerator:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def generate(
        self,
        *,
        requested_by: UUID,
        context: QuizContext,
        kind: QuestionKind,
        n: int,
        skip: int = 0,
    ) -> list[QuestionDraft]:
        data = await self._llm.complete_json(
            system=SYSTEM_PROMPT,
            prompt=(
                f"Escribe {n} {KIND_RULES[kind]}, de opción múltiple con 3 opciones y una sola "
                "correcta, con retroalimentación amable para el acierto y para el error.\n\n"
                f"Material «{context.material_title}»:\n<<<\n"
                f"{context.material_text[:MAX_MATERIAL_CHARS]}\n>>>\n\n"
                'Responde con este JSON: {"questions": [{"statement": str, "options": [str], '
                '"correct_index": int, "feedback_correct": str, "feedback_wrong": str}]}.'
            ),
        )
        parsed = _QuizJson.model_validate(data)
        drafts = []
        for q in parsed.questions[:n]:
            letters = "abcd"[: len(q.options)]
            if q.correct_index >= len(q.options):
                raise InvalidQuestion("correct_index out of range")
            drafts.append(
                QuestionDraft(
                    statement=q.statement,
                    options=tuple(Option(letters[i], t) for i, t in enumerate(q.options)),
                    correct_option=letters[q.correct_index],
                    feedback_correct=q.feedback_correct,
                    feedback_wrong=q.feedback_wrong,
                ).shuffled()
            )
        return drafts


class ResilientQuestionGenerator:
    def __init__(
        self,
        primary: LlmQuestionGenerator,
        fallback: FallbackQuestionGenerator,
        limiter: RateLimiter,
        timeout_seconds: float,
    ) -> None:
        self._primary, self._fallback = primary, fallback
        self._limiter, self._timeout = limiter, timeout_seconds

    async def generate(
        self,
        *,
        requested_by: UUID,
        context: QuizContext,
        kind: QuestionKind,
        n: int,
        skip: int = 0,
    ) -> list[QuestionDraft]:
        result, _ = await call_with_fallback(
            lambda: self._primary.generate(
                requested_by=requested_by, context=context, kind=kind, n=n, skip=skip
            ),
            lambda: self._fallback.generate(
                requested_by=requested_by, context=context, kind=kind, n=n, skip=skip
            ),
            timeout_seconds=self._timeout,
            allowed=await self._limiter.allow(requested_by),
        )
        return result


__all__ = [
    "FallbackQuestionGenerator",
    "LlmQuestionGenerator",
    "ResilientQuestionGenerator",
]
