"""Scoring and running prompts: the model first (15 s cap), deterministic fallbacks otherwise.

- ``RubricScorer`` scores with the domain rubric (no AI).
- ``SimulatedRunner`` cannot really run a prompt without a model, so it shows the difference the
  recipe makes using only the person's material: a generic dump for a vague prompt, a short
  answer in the requested shape for a complete one. The response says ``fallback: true``.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.prompt_coach.application.ports import MaterialContext, RunOutput, ScoreDraft
from frobi.modules.prompt_coach.domain import RecipePiece, improve, score_prompt
from frobi.shared.domain import text
from frobi.shared.infrastructure.llm import (
    SYSTEM_PROMPT,
    LlmClient,
    RateLimiter,
    call_with_fallback,
)

MAX_MATERIAL_CHARS = 20_000


# --- Scoring -------------------------------------------------------------------------------


class RubricScorer:
    async def score(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> ScoreDraft:
        scores = score_prompt(prompt)
        return ScoreDraft(
            scores=scores,
            feedback={},
            improved_text=improve(prompt, scores, material.title if material else None),
        )


class _PieceJson(BaseModel):
    score: int = Field(ge=0, le=4)
    feedback: str = Field(min_length=1, max_length=300)


class _ScoreJson(BaseModel):
    context: _PieceJson
    goal: _PieceJson
    level: _PieceJson
    format: _PieceJson
    improved_text: str = Field(min_length=1, max_length=4000)


SCORE_INSTRUCTIONS = (
    "Evalúa la instrucción que una persona le daría a una IA según 4 piezas: contexto (quién es "
    "y de qué material habla), objetivo (qué quiere lograr), nivel (qué sabe ya o cómo quiere "
    "que se lo expliquen) y formato (cómo quiere la respuesta). Puntúa cada pieza de 0 a 4 con "
    "una retroalimentación breve y amable, y escribe una versión mejorada que conserve sus "
    'palabras. Responde con este JSON: {"context": {"score": int, "feedback": str}, "goal": …, '
    '"level": …, "format": …, "improved_text": str}.'
)


class LlmScorer:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def score(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> ScoreDraft:
        about = f"\nMaterial de referencia: «{material.title}»." if material else ""
        data = await self._llm.complete_json(
            system=SYSTEM_PROMPT,
            prompt=f"{SCORE_INSTRUCTIONS}{about}\n\nInstrucción:\n<<<\n{prompt}\n>>>",
        )
        parsed = _ScoreJson.model_validate(data)
        pieces = {p: getattr(parsed, p.value) for p in RecipePiece}
        return ScoreDraft(
            scores={p: v.score for p, v in pieces.items()},
            feedback={p: v.feedback for p, v in pieces.items()},
            improved_text=parsed.improved_text,
        )


class ResilientScorer:
    def __init__(
        self, primary: LlmScorer, fallback: RubricScorer, limiter: RateLimiter, timeout: float
    ) -> None:
        self._primary, self._fallback = primary, fallback
        self._limiter, self._timeout = limiter, timeout

    async def score(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> ScoreDraft:
        result, _ = await call_with_fallback(
            lambda: self._primary.score(
                requested_by=requested_by, prompt=prompt, material=material
            ),
            lambda: self._fallback.score(
                requested_by=requested_by, prompt=prompt, material=material
            ),
            timeout_seconds=self._timeout,
            allowed=await self._limiter.allow(requested_by),
        )
        return result


# --- Running -------------------------------------------------------------------------------


def _content_sentences(material_text: str) -> list[str]:
    lines = [line for line in material_text.splitlines() if line and not line.startswith("#")]
    return text.sentences(" ".join(lines))


def _shorten(sentence: str, words: int = 18) -> str:
    parts = sentence.split()
    return sentence if len(parts) <= words else " ".join(parts[:words]) + "…"


def simulate(prompt: str, material: MaterialContext | None) -> str:
    scores = score_prompt(prompt)
    shaped = scores[RecipePiece.FORMAT] >= 3 or scores[RecipePiece.LEVEL] >= 3
    if material is None:
        if shaped:
            return (
                "Una respuesta pensada para ti: con el nivel y el formato que pediste, "
                "fácil de revisar punto por punto."
            )
        return (
            "Una respuesta general y larga sobre el tema, sin saber qué necesitas, qué sabes ya "
            "ni cómo te conviene leerla."
        )
    sentences = _content_sentences(material.text)
    if not sentences:
        return material.text[:400]
    if not shaped:
        return " ".join(sentences[:4])
    wanted = text.keywords(prompt)
    ranked = sorted(sentences, key=lambda s: -len(wanted & text.keywords(s)))
    return "\n".join(f"• {_shorten(s)}" for s in ranked[:3])


class SimulatedRunner:
    async def run(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> RunOutput:
        return RunOutput(text=simulate(prompt, material), fallback=True)


class _RunJson(BaseModel):
    text: str = Field(min_length=1, max_length=8000)


class LlmRunner:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def run(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> RunOutput:
        source = (
            f"\n\nMaterial «{material.title}»:\n<<<\n{material.text[:MAX_MATERIAL_CHARS]}\n>>>"
            if material
            else ""
        )
        data = await self._llm.complete_json(
            system=SYSTEM_PROMPT,
            prompt=f'{prompt}{source}\n\nResponde con este JSON: {{"text": str}}.',
        )
        return RunOutput(text=_RunJson.model_validate(data).text, fallback=False)


class ResilientRunner:
    def __init__(
        self, primary: LlmRunner, fallback: SimulatedRunner, limiter: RateLimiter, timeout: float
    ) -> None:
        self._primary, self._fallback = primary, fallback
        self._limiter, self._timeout = limiter, timeout

    async def run(
        self, *, requested_by: UUID, prompt: str, material: MaterialContext | None
    ) -> RunOutput:
        result, _ = await call_with_fallback(
            lambda: self._primary.run(requested_by=requested_by, prompt=prompt, material=material),
            lambda: self._fallback.run(requested_by=requested_by, prompt=prompt, material=material),
            timeout_seconds=self._timeout,
            allowed=await self._limiter.allow(requested_by),
        )
        return result
