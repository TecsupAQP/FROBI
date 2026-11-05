"""PdfTextExtractor on pypdf. Parsing is CPU-bound, so it runs in a worker thread.

Besides the text of each page it reads what tells the topics apart at no AI cost: the outline
(bookmarks) and the lines written in a font clearly bigger than the body text.
"""

import asyncio
import math
from collections import Counter
from io import BytesIO
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from frobi.modules.materials.application.ports import OutlineEntry, PdfContent
from frobi.modules.materials.domain import PdfUnreadable

MAX_PAGES = 200
# A line counts as a heading from this many times the body font size.
HEADING_SCALE = 1.25
MAX_HEADING_CHARS = 90


def _outline(reader: PdfReader) -> tuple[OutlineEntry, ...]:
    entries: list[OutlineEntry] = []

    def walk(items: list[Any], level: int) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item, level + 1)
                continue
            try:
                page = reader.get_destination_page_number(item)
            except (PyPdfError, ValueError, KeyError, TypeError, AttributeError):
                continue
            title = str(getattr(item, "title", "") or "").strip()
            if title and page is not None and 0 <= page < MAX_PAGES:
                entries.append(OutlineEntry(title=title, page=page, level=level))

    try:
        walk(list(reader.outline), 0)
    except (PyPdfError, ValueError, KeyError, TypeError, AttributeError):
        return ()
    return tuple(entries)


def _page_lines(page: Any) -> tuple[str, list[tuple[str, float]]]:
    """The page text and each of its lines with the font size most of its characters use."""
    runs: list[tuple[str, float]] = []

    def visitor(text: str, cm: list[float], tm: list[float], _font: Any, size: float) -> None:
        if text:
            scale = math.hypot(tm[2], tm[3]) * math.hypot(cm[2], cm[3]) or 1.0
            runs.append((text, abs(size * scale)))

    text = page.extract_text(visitor_text=visitor) or ""
    lines: list[tuple[str, float]] = []
    current: list[str] = []
    sizes: Counter[float] = Counter()
    for run_text, size in runs:
        pieces = run_text.split("\n")
        for index, piece in enumerate(pieces):
            if piece:
                current.append(piece)
                sizes[round(size, 1)] += len(piece)
            if index < len(pieces) - 1 and current:
                lines.append(("".join(current).strip(), sizes.most_common(1)[0][0]))
                current, sizes = [], Counter()
    if current:
        lines.append(("".join(current).strip(), sizes.most_common(1)[0][0]))
    return text, [(line, size) for line, size in lines if line]


def _headings(pages: list[list[tuple[str, float]]]) -> tuple[tuple[int, str], ...]:
    weights: Counter[float] = Counter()
    for lines in pages:
        for line, size in lines:
            weights[size] += len(line)
    if not weights:
        return ()
    body = weights.most_common(1)[0][0]
    if body <= 0:
        return ()
    return tuple(
        (index, line)
        for index, lines in enumerate(pages)
        for line, size in lines
        if size >= body * HEADING_SCALE
        and len(line) <= MAX_HEADING_CHARS
        and sum(c.isalpha() for c in line) >= 3
    )


def _extract(data: bytes) -> PdfContent:
    if not data.lstrip()[:5].startswith(b"%PDF"):
        raise PdfUnreadable()
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise PdfUnreadable("Ese PDF tiene contraseña. Quítala o pega el texto.")
        texts: list[str] = []
        lines: list[list[tuple[str, float]]] = []
        for page in reader.pages[:MAX_PAGES]:
            try:
                text, page_lines = _page_lines(page)
            except (PyPdfError, ValueError, KeyError, TypeError, ZeroDivisionError):
                # Font sizes are a bonus: a page that fails with the visitor still gives its text.
                text, page_lines = page.extract_text() or "", []
            texts.append(text)
            lines.append(page_lines)
        return PdfContent(pages=tuple(texts), outline=_outline(reader), headings=_headings(lines))
    except PdfUnreadable:
        raise
    except (PyPdfError, ValueError, KeyError, TypeError, OSError) as error:
        raise PdfUnreadable() from error


class PypdfTextExtractor:
    async def extract(self, data: bytes) -> PdfContent:
        return await asyncio.to_thread(_extract, data)
