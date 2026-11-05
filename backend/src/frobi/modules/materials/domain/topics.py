"""Split a material into study topics of a size the AI can take (RF01, RF02, RNF06).

Every format (visual map, real example, easy read, audio), hint and question works on **one
topic**, never on the whole document: a 200-page PDF costs the same per request as a 2-page one.

Boundaries come from the document's own structure first (outline, larger fonts, headings in the
text) and only then from the AI. Whatever their source, topics are kept between
``MIN_TOPIC_CHARS`` and ``MAX_TOPIC_CHARS``: tiny ones join the previous topic and long ones are
cut at paragraph breaks into «(parte 2)», «(parte 3)»…
"""

import itertools
import re
from bisect import bisect_right
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import median

# ~1 500 tokens: one topic plus the recipe and the answer fit easily in the 15 s cap.
MAX_TOPIC_CHARS = 6_000
MIN_TOPIC_CHARS = 300
MAX_TOPICS = 120
TITLE_MAX = 80
# Numbered or capitalised lines only count as headings when they are this far apart on
# average: closer than that they are a list, not chapters.
MIN_HEADING_SPACING = 800

WHOLE_MATERIAL = "Todo el material"
INTRODUCTION = "Introducción"

_MARKDOWN = re.compile(r"^#{1,3}\s+(?P<title>\S.*)$")
_KEYWORD = re.compile(
    r"^(cap[ií]tulo|unidad|tema|m[oó]dulo|lecci[oó]n|secci[oó]n|parte|semana|sesi[oó]n)"
    r"\s+([0-9]{1,3}|[IVXLC]{1,6})\b",
    re.IGNORECASE,
)
_NUMBERED = re.compile(r"^(\d{1,2}(\.\d{1,2})?)[.)]?\s+\S")


@dataclass(frozen=True, slots=True)
class Boundary:
    """A topic starts at ``offset`` (in the material's text) with this title."""

    offset: int
    title: str


@dataclass(frozen=True, slots=True)
class TopicSpan:
    title: str
    start: int
    end: int
    page_start: int | None = None
    page_end: int | None = None


@dataclass(frozen=True, slots=True)
class Topic:
    position: int
    title: str
    text: str
    page_start: int | None = None
    page_end: int | None = None


def clean_title(raw: str) -> str:
    title = " ".join(raw.replace("#", " ").split()).strip(" .:-–—")
    return title[: TITLE_MAX - 1].rstrip() + "…" if len(title) > TITLE_MAX else title


def _lines(text: str) -> list[tuple[int, str, bool]]:
    """(offset, line, starts a paragraph) for every non-empty line."""
    found: list[tuple[int, str, bool]] = []
    offset = 0
    previous_blank = True
    for line in text.split("\n"):
        if line.strip():
            found.append((offset, line.strip(), previous_blank))
        previous_blank = not line.strip()
        offset += len(line) + 1
    return found


def _spaced(boundaries: list[Boundary], text_length: int) -> bool:
    if len(boundaries) < 2:
        return False
    gaps = [b.offset - a.offset for a, b in itertools.pairwise(boundaries)]
    gaps.append(text_length - boundaries[-1].offset)
    return median(gaps) >= MIN_HEADING_SPACING


def _is_caps_heading(line: str) -> bool:
    letters = [c for c in line if c.isalpha()]
    return 4 <= len(line) <= TITLE_MAX and len(letters) >= 4 and line.upper() == line


def text_heading_boundaries(text: str) -> list[Boundary]:
    """Headings written in the text itself, from the most to the least explicit kind."""
    lines = _lines(text)
    markdown = [
        Boundary(offset, clean_title(match["title"]))
        for offset, line, _ in lines
        if (match := _MARKDOWN.match(line))
    ]
    if len(markdown) >= 2:
        return markdown
    short_starts = [
        (offset, line)
        for offset, line, starts in lines
        if starts and len(line) <= TITLE_MAX and not line.endswith((".", ",", ";"))
    ]
    keyword = [Boundary(o, clean_title(line)) for o, line in short_starts if _KEYWORD.match(line)]
    if len(keyword) >= 2:
        return keyword
    numbered = [
        Boundary(o, clean_title(line))
        for o, line in short_starts
        if (match := _NUMBERED.match(line)) and "." not in match.group(1)
    ]
    if _spaced(numbered, len(text)):
        return numbered
    caps = [
        Boundary(o, clean_title(line.capitalize()))
        for o, line in short_starts
        if _is_caps_heading(line)
    ]
    if _spaced(caps, len(text)):
        return caps
    return []


def locate_titles(
    text: str,
    page_offsets: Sequence[int],
    titles: Sequence[tuple[int, str]],
    *,
    page_start_if_missing: bool,
) -> list[Boundary]:
    """Places (page index, title) pairs in the text: at the line that reads like the title on
    that page, or at the start of the page when it is not found and ``page_start_if_missing``."""
    found: list[Boundary] = []
    for page, raw_title in titles:
        title = clean_title(raw_title)
        if not title or not 0 <= page < len(page_offsets):
            continue
        start = page_offsets[page]
        end = page_offsets[page + 1] if page + 1 < len(page_offsets) else len(text)
        wanted = " ".join(title.lower().split())
        offset = next(
            (
                start + o
                for o, line, _ in _lines(text[start:end])
                if " ".join(line.lower().split()).startswith(wanted[:40])
            ),
            None,
        )
        if offset is None and page_start_if_missing:
            offset = start
        if offset is not None:
            found.append(Boundary(offset, title))
    return found


def paragraph_starts(text: str) -> list[int]:
    starts = [0]
    for match in re.finditer(r"\n\s*\n", text):
        if match.end() < len(text):
            starts.append(match.end())
    return starts


def skeleton(text: str, *, max_blocks: int = 400, label_chars: int = 90) -> list[tuple[int, str]]:
    """(offset, first words) of each paragraph — or of groups of paragraphs when there are more
    than ``max_blocks``. This is all the AI reads to find topics, never the whole text."""
    starts = paragraph_starts(text)
    step = max(1, -(-len(starts) // max_blocks))
    blocks = starts[::step]
    return [
        (offset, " ".join(text[offset : offset + label_chars * 2].split())[:label_chars])
        for offset in blocks
    ]


def _first_words(text: str) -> str:
    sentence = re.split(r"(?<=[.!?])\s", " ".join(text.split()), maxsplit=1)[0]
    words = sentence.split()
    return clean_title(" ".join(words[:8]) + ("…" if len(words) > 8 else ""))


def _cut(text: str, start: int, end: int) -> list[int]:
    """Cut points in [start, end) so no piece is longer than MAX_TOPIC_CHARS, at paragraph
    breaks when possible (then at a sentence end, then anywhere)."""
    cuts = [start]
    while end - cuts[-1] > MAX_TOPIC_CHARS:
        piece_start = cuts[-1]
        limit = piece_start + MAX_TOPIC_CHARS
        window = text[piece_start + MIN_TOPIC_CHARS : limit]
        paragraph = window.rfind("\n\n")
        sentence = max(window.rfind(". "), window.rfind(".\n"))
        if paragraph >= 0:
            cut = piece_start + MIN_TOPIC_CHARS + paragraph + 2
        elif sentence >= 0:
            cut = piece_start + MIN_TOPIC_CHARS + sentence + 2
        else:
            cut = limit
        cuts.append(cut)
    return cuts


def _size(text: str, span: tuple[str, int, int]) -> int:
    return len(text[span[1] : span[2]].strip())


def spans_from_boundaries(
    text: str, boundaries: Sequence[Boundary], page_offsets: Sequence[int] = ()
) -> tuple[TopicSpan, ...]:
    """Topics from boundaries in any order, with every size rule applied. With no boundaries a
    short text is one topic and a long one is cut into parts titled by their first words."""
    length = len(text)
    if not text.strip():
        return ()
    ordered = sorted(
        {b.offset: b for b in boundaries if 0 <= b.offset < length and b.title}.values(),
        key=lambda b: b.offset,
    )
    raw: list[tuple[str, int, int]] = []
    if not ordered:
        raw = [(WHOLE_MATERIAL, 0, length)]
    else:
        if ordered[0].offset > 0:
            if len(text[: ordered[0].offset].strip()) >= MIN_TOPIC_CHARS:
                raw.append((INTRODUCTION, 0, ordered[0].offset))
            else:
                ordered[0] = Boundary(0, ordered[0].title)
        for index, boundary in enumerate(ordered):
            end = ordered[index + 1].offset if index + 1 < len(ordered) else length
            raw.append((boundary.title, boundary.offset, end))

    # Tiny topics join the previous one (or the next, at the very start).
    merged: list[tuple[str, int, int]] = []
    carry: int | None = None
    for title, start, end in raw:
        if carry is not None:
            start, carry = carry, None
        if _size(text, (title, start, end)) < MIN_TOPIC_CHARS:
            if merged:
                previous = merged[-1]
                merged[-1] = (previous[0], previous[1], end)
            else:
                carry = start
            continue
        merged.append((title, start, end))
    if carry is not None:
        merged = [(raw[-1][0] if len(raw) == 1 else WHOLE_MATERIAL, carry, length)]

    # Long topics are cut into parts.
    sized: list[tuple[str, int, int]] = []
    unnamed = not ordered
    for title, start, end in merged:
        cuts = _cut(text, start, end)
        for part, cut in enumerate(cuts):
            piece_end = cuts[part + 1] if part + 1 < len(cuts) else end
            if unnamed and len(cuts) > 1:
                name = f"Parte {len(sized) + 1}: {_first_words(text[cut:piece_end])}"
            elif len(cuts) > 1:
                name = f"{title} (parte {part + 1})"
            else:
                name = title
            sized.append((clean_title(name), cut, piece_end))

    # Too many topics: join neighbours while they still fit in one request.
    while len(sized) > MAX_TOPICS:
        pairs = [
            (sized[i + 1][2] - sized[i][1], i)
            for i in range(len(sized) - 1)
            if sized[i + 1][2] - sized[i][1] <= MAX_TOPIC_CHARS
        ]
        if not pairs:
            break
        _, i = min(pairs)
        sized[i : i + 2] = [(sized[i][0], sized[i][1], sized[i + 1][2])]

    def page_of(offset: int) -> int | None:
        return bisect_right(page_offsets, offset) if page_offsets else None

    return tuple(
        TopicSpan(title, start, end, page_of(start), page_of(max(start, end - 1)))
        for title, start, end in sized
    )


def topics_of(text: str, spans: Sequence[TopicSpan]) -> tuple[Topic, ...]:
    return tuple(
        Topic(
            position=index + 1,
            title=span.title,
            text=text[span.start : span.end].strip(),
            page_start=span.page_start,
            page_end=span.page_end,
        )
        for index, span in enumerate(spans)
    )
