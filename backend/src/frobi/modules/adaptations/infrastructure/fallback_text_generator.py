"""Answers without AI (RF29, RNF06): prewritten for the sample guide, rule-based for the rest.

The rule-based version only reorganizes and shortens the person's own text; it never adds facts.
"""

import json
import re
from functools import cache
from pathlib import Path
from uuid import UUID

from frobi.modules.adaptations.application.ports import Generated, SourceMaterial
from frobi.modules.adaptations.domain import AdaptedContent, Format, Recipe, Section

from .content_codec import content_from_json

FALLBACKS_DIR = Path(__file__).parent / "fallbacks"
_SENTENCE = re.compile(r"(?<=[.!?])\s+")
MAX_SECTIONS = 8


@cache
def _prewritten() -> dict[tuple[UUID, Format], AdaptedContent]:
    table: dict[tuple[UUID, Format], AdaptedContent] = {}
    for path in sorted(FALLBACKS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        material_id = UUID(data["material_id"])
        for fmt, content in data["formats"].items():
            table[(material_id, Format(fmt))] = content_from_json(content)
    return table


def _sections(text: str) -> list[tuple[str, str]]:
    """Split on ``#`` headings; without headings, each paragraph is a part."""
    blocks: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            blocks.append((stripped.lstrip("#").strip(), []))
        elif stripped:
            if not blocks:
                blocks.append(("", []))
            blocks[-1][1].append(stripped)
    if len(blocks) == 1 and not blocks[0][0]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return [(f"Parte {n}", p) for n, p in enumerate(paragraphs, start=1)][:MAX_SECTIONS]
    return [(h or "Introducción", " ".join(lines)) for h, lines in blocks][:MAX_SECTIONS]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE.split(text) if s.strip()]


def _shorten(sentence: str, max_words: int) -> str:
    words = sentence.split()
    if len(words) <= max_words:
        return sentence
    return " ".join(words[:max_words]).rstrip(",;:") + "…"


def rule_based(material: SourceMaterial, fmt: Format) -> AdaptedContent:
    sections: list[Section] = []
    for heading, body in _sections(material.text):
        sentences = _sentences(body) or [body]
        if fmt is Format.EASY_READ:
            section = Section(heading, " ".join(_shorten(s, 16) for s in sentences[:3]))
        elif fmt is Format.VISUAL_MAP:
            section = Section(
                heading,
                _shorten(sentences[0], 14),
                tuple(_shorten(s, 10) for s in sentences[1:5]),
            )
        elif fmt is Format.REAL_EXAMPLE:
            section = Section(
                heading,
                _shorten(sentences[0], 20),
                (f"Piensa en un caso de tu carrera donde aparezca «{heading.lower()}».",),
            )
        else:
            section = Section(heading, " ".join(_shorten(s, 24) for s in sentences[:4]))
        sections.append(section)
    if not sections:
        sections.append(Section("Tu material", _shorten(material.text, 60)))
    return AdaptedContent(title=material.title, sections=tuple(sections))


class FallbackTextGenerator:
    async def adapt(
        self, *, requested_by: UUID, material: SourceMaterial, recipe: Recipe
    ) -> Generated:
        prewritten = _prewritten().get((material.id, recipe.format))
        content = prewritten or rule_based(material, recipe.format)
        return Generated(content=content, fallback=True)
