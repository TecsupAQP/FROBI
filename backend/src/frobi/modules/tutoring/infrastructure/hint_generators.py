"""Help for each step: the model first (15 s cap), then help built from the material, no AI.

The no-AI help only points to and quotes the person's own material; it never invents facts.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.tutoring.application.ports import Hint, TutoringContext
from frobi.modules.tutoring.domain import HelpStep, Section, most_relevant_section
from frobi.shared.domain import text
from frobi.shared.infrastructure.llm import (
    SYSTEM_PROMPT,
    LlmClient,
    RateLimiter,
    call_with_fallback,
)

# One section is already small (materials keeps topics under ~6 000 characters); this only
# guards older materials that are a single long section.
MAX_MATERIAL_CHARS = 8_000
STEP_RULES: dict[HelpStep, str] = {
    HelpStep.HINT_1: "Da una sola pista que oriente hacia dónde mirar. No des la respuesta.",
    HelpStep.HINT_2: "Da una pista más concreta, con una idea clave del material. No des la "
    "respuesta.",
    HelpStep.STEP_BY_STEP: "Explica los pasos para resolverlo, sin escribir el resultado final.",
    HelpStep.FINAL: "Da la respuesta completa, explica por qué y pide comparar con el intento.",
}


def _best_sentence(task: str, section: Section) -> str:
    wanted = text.keywords(task)
    candidates = [s for p in section.paragraphs for s in text.sentences(p)]
    if not candidates:
        return section.heading
    return max(candidates, key=lambda s: len(wanted & text.keywords(s)))


def _start_of(sentence: str, words: int = 8) -> str:
    parts = sentence.split()
    return sentence if len(parts) <= words else " ".join(parts[:words]) + "…"


def material_hint(context: TutoringContext, task_ref: str, step: HelpStep) -> str:
    section = most_relevant_section(task_ref, context.material_text)
    if section is None:
        return "Vuelve a leer tu material con calma y anota la idea principal."
    sentence = _best_sentence(task_ref, section)
    if step is HelpStep.HINT_1:
        return (
            f"Vuelve a leer la parte «{section.heading}» de tu material. "
            "¿Qué dice sobre lo que te pide la tarea?"
        )
    if step is HelpStep.HINT_2:
        return f"Fíjate en esta idea de «{section.heading}»: «{_start_of(sentence)}»"
    if step is HelpStep.STEP_BY_STEP:
        return (
            "1. Escribe con tus palabras qué te pide la tarea. "
            f"2. Lee la parte «{section.heading}». "
            "3. Subraya la frase que responde a lo que te piden. "
            "4. Arma tu respuesta y compárala con la guía."
        )
    return (
        f"Según tu material («{section.heading}»): «{sentence}» "
        "Compáralo con tu intento: ¿en qué se parecen y en qué no?"
    )


class FallbackHintGenerator:
    async def hint(
        self, *, requested_by: UUID, context: TutoringContext, task_ref: str, step: HelpStep
    ) -> Hint:
        return Hint(text=material_hint(context, task_ref, step), fallback=True)


class HintJson(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


def relevant_text(context: TutoringContext, task_ref: str) -> str:
    """The section of the guide the task is about: all the AI needs to read for a hint."""
    section = most_relevant_section(task_ref, context.material_text)
    if section is None:
        return context.material_text[:MAX_MATERIAL_CHARS]
    return f"## {section.heading}\n" + "\n".join(section.paragraphs)[:MAX_MATERIAL_CHARS]


def build_prompt(context: TutoringContext, task_ref: str, step: HelpStep) -> str:
    return (
        f"Tarea: {task_ref}\n"
        f"Escalón de ayuda: {step.value}. {STEP_RULES[step]}\n\n"
        f"Parte del material «{context.material_title}» que trata la tarea:\n<<<\n"
        f"{relevant_text(context, task_ref)}\n>>>\n\n"
        'Responde con este JSON: {"text": str}.'
    )


class LlmHintGenerator:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def hint(
        self, *, requested_by: UUID, context: TutoringContext, task_ref: str, step: HelpStep
    ) -> Hint:
        data = await self._llm.complete_json(
            system=SYSTEM_PROMPT, prompt=build_prompt(context, task_ref, step)
        )
        return Hint(text=HintJson.model_validate(data).text, fallback=False)


class ResilientHintGenerator:
    def __init__(
        self,
        primary: LlmHintGenerator,
        fallback: FallbackHintGenerator,
        limiter: RateLimiter,
        timeout_seconds: float,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._limiter = limiter
        self._timeout = timeout_seconds

    async def hint(
        self, *, requested_by: UUID, context: TutoringContext, task_ref: str, step: HelpStep
    ) -> Hint:
        result, _ = await call_with_fallback(
            lambda: self._primary.hint(
                requested_by=requested_by, context=context, task_ref=task_ref, step=step
            ),
            lambda: self._fallback.hint(
                requested_by=requested_by, context=context, task_ref=task_ref, step=step
            ),
            timeout_seconds=self._timeout,
            allowed=await self._limiter.allow(requested_by),
        )
        return result
