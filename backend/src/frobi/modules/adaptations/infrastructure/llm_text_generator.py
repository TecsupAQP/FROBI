"""TextGenerator on the shared LLM client, with the 15 s cap, rate limit and fallback."""

from uuid import UUID

from frobi.modules.adaptations.application.ports import Generated, SourceMaterial
from frobi.modules.adaptations.domain import Recipe
from frobi.shared.infrastructure.llm import (
    SYSTEM_PROMPT,
    LlmClient,
    RateLimiter,
    call_with_fallback,
)

from .content_codec import content_from_json
from .fallback_text_generator import FallbackTextGenerator

MAX_MATERIAL_CHARS = 20_000
OUTPUT_SHAPE = (
    'Responde con este JSON: {"title": str, "sections": '
    '[{"heading": str, "body": str, "items": [str]}]}. Entre 3 y 5 secciones; cada "body" de '
    "1 a 3 frases cortas y como máximo 3 items breves por sección. "
    "Sé breve: no más de 250 palabras en total."
)


def build_prompt(material: SourceMaterial, recipe: Recipe) -> str:
    """The recipe the person sees, then the material, then the output shape."""
    return (
        f"{recipe.prompt_text()}\n\n"
        f"Material «{material.title}»:\n<<<\n{material.text[:MAX_MATERIAL_CHARS]}\n>>>\n\n"
        f"{OUTPUT_SHAPE}"
    )


class LlmTextGenerator:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def adapt(
        self, *, requested_by: UUID, material: SourceMaterial, recipe: Recipe
    ) -> Generated:
        data = await self._llm.complete_json(
            system=SYSTEM_PROMPT, prompt=build_prompt(material, recipe)
        )
        # An invalid shape raises here and counts as a failure: the fallback answers instead.
        return Generated(content=content_from_json(data), fallback=False)


class ResilientTextGenerator:
    """Model first, never longer than the cap; prewritten/rule-based answer otherwise."""

    def __init__(
        self,
        primary: LlmTextGenerator,
        fallback: FallbackTextGenerator,
        limiter: RateLimiter,
        timeout_seconds: float,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._limiter = limiter
        self._timeout = timeout_seconds

    async def adapt(
        self, *, requested_by: UUID, material: SourceMaterial, recipe: Recipe
    ) -> Generated:
        result, _ = await call_with_fallback(
            lambda: self._primary.adapt(
                requested_by=requested_by, material=material, recipe=recipe
            ),
            lambda: self._fallback.adapt(
                requested_by=requested_by, material=material, recipe=recipe
            ),
            timeout_seconds=self._timeout,
            allowed=await self._limiter.allow(requested_by),
        )
        return result
