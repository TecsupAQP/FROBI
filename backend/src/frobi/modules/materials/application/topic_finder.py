"""Find a material's topics spending as few tokens as possible.

1. The PDF's own outline (bookmarks): free and what the author meant.
2. Lines written in a bigger font than the body: free.
3. Headings in the text (``##``, «Unidad 2», numbered or capitalised titles): free.
4. Only for a long text with none of that: the AI reads its skeleton (the first words of each
   paragraph, a few thousand tokens at most) and says where each topic starts.
5. Without the AI: parts of the right size, titled by their first words.
"""

import logging
from collections.abc import Sequence

from frobi.modules.materials.application.ports import OutlineEntry, TopicSegmenter
from frobi.modules.materials.domain import (
    MAX_TOPIC_CHARS,
    Boundary,
    TopicSpan,
    locate_titles,
    skeleton,
    spans_from_boundaries,
    text_heading_boundaries,
)

logger = logging.getLogger(__name__)


def _outline_titles(outline: Sequence[OutlineEntry]) -> list[tuple[int, str]]:
    """Top-level bookmarks; one level deeper when the top level is a single «book» entry."""
    for level in (0, 1):
        entries = [(e.page, e.title) for e in outline if e.level <= level]
        if len(entries) >= 2:
            return entries
    return []


class TopicFinder:
    def __init__(self, segmenter: TopicSegmenter | None = None) -> None:
        self._segmenter = segmenter

    async def find(
        self,
        title: str,
        text: str,
        *,
        page_offsets: Sequence[int] = (),
        outline: Sequence[OutlineEntry] = (),
        headings: Sequence[tuple[int, str]] = (),
    ) -> tuple[TopicSpan, ...]:
        boundaries = self._structure(text, page_offsets, outline, headings)
        if not boundaries and len(text) > MAX_TOPIC_CHARS * 1.5:
            boundaries = await self._ask_ai(title, text)
        return spans_from_boundaries(text, boundaries, page_offsets)

    def _structure(
        self,
        text: str,
        page_offsets: Sequence[int],
        outline: Sequence[OutlineEntry],
        headings: Sequence[tuple[int, str]],
    ) -> list[Boundary]:
        if page_offsets:
            from_outline = locate_titles(
                text, page_offsets, _outline_titles(outline), page_start_if_missing=True
            )
            if len(from_outline) >= 2:
                return from_outline
            from_fonts = locate_titles(
                text, page_offsets, list(headings), page_start_if_missing=False
            )
            if len(from_fonts) >= 2:
                return from_fonts
        return text_heading_boundaries(text)

    async def _ask_ai(self, title: str, text: str) -> list[Boundary]:
        if self._segmenter is None:
            return []
        blocks = skeleton(text)
        try:
            found = await self._segmenter.segment(title, [label for _, label in blocks])
        except Exception:
            logger.warning("Topic segmentation failed; cutting by size", exc_info=True)
            return []
        if not found:
            return []
        return [
            Boundary(blocks[index][0], topic_title)
            for index, topic_title in found
            if 0 <= index < len(blocks)
        ]
