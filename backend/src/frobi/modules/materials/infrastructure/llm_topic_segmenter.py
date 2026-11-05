"""TopicSegmenter on the shared LLM client: one cheap call per long, unstructured material.

The model never reads the whole text, only its skeleton (the first words of each paragraph,
numbered), and answers where each topic starts. Any failure or timeout returns None and the
material is cut by size instead.
"""

import asyncio
from collections.abc import Sequence

from pydantic import BaseModel, Field, ValidationError

from frobi.shared.infrastructure.llm import SYSTEM_PROMPT, LlmClient, LlmUnavailable

MAX_TOPICS = 40
INSTRUCTIONS = (
    "Este es el esqueleto de un material de estudio: cada línea es el inicio de un bloque, con "
    "su número entre corchetes. Divídelo en temas de estudio: cada tema empieza donde cambia "
    "la idea principal. Usa entre 2 y {max_topics} temas, en orden, y el primero empieza en "
    'el bloque 0. Responde con este JSON: {{"topics": [{{"start": int, "title": str}}]}}. '
    "Cada título, en español, de 2 a 8 palabras y fiel al contenido."
)


class _TopicJson(BaseModel):
    start: int = Field(ge=0)
    title: str = Field(min_length=1, max_length=120)


class _TopicsJson(BaseModel):
    topics: list[_TopicJson] = Field(min_length=2, max_length=MAX_TOPICS)


class LlmTopicSegmenter:
    def __init__(self, llm: LlmClient, timeout_seconds: float) -> None:
        self._llm = llm
        self._timeout = timeout_seconds

    async def segment(self, title: str, blocks: Sequence[str]) -> list[tuple[int, str]] | None:
        lines = "\n".join(f"[{index}] {label}" for index, label in enumerate(blocks))
        prompt = (
            INSTRUCTIONS.format(max_topics=MAX_TOPICS)
            + f"\n\nMaterial «{title}»:\n<<<\n{lines}\n>>>"
        )
        try:
            data = await asyncio.wait_for(
                self._llm.complete_json(system=SYSTEM_PROMPT, prompt=prompt), self._timeout
            )
            parsed = _TopicsJson.model_validate(data)
        except (TimeoutError, LlmUnavailable, ValidationError):
            return None
        starts = sorted({t.start: t.title for t in parsed.topics if t.start < len(blocks)}.items())
        return starts if len(starts) >= 2 else None
