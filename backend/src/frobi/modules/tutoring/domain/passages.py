"""Find the passages of the guide that an answer talks about — text search only, no AI (RF41)."""

from dataclasses import dataclass

from frobi.shared.domain import text

MAX_PASSAGES = 3


@dataclass(frozen=True, slots=True)
class Passage:
    text: str
    location: str


@dataclass(frozen=True, slots=True)
class Section:
    heading: str
    paragraphs: tuple[str, ...]


def sections_of(material_text: str) -> list[Section]:
    """``#`` headings split sections; text before any heading is «Introducción»."""
    sections: list[tuple[str, list[str]]] = []
    for line in material_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            sections.append((stripped.lstrip("#").strip(), []))
        elif stripped:
            if not sections:
                sections.append(("Introducción", []))
            sections[-1][1].append(stripped)
    return [Section(heading, tuple(paragraphs)) for heading, paragraphs in sections]


def find_passages(answer: str, material_title: str, material_text: str) -> list[Passage]:
    """Sentences sharing at least 2 keywords with the answer (or all of them, if it has 1)."""
    wanted = text.keywords(answer)
    if not wanted:
        return []
    needed = min(2, len(wanted))
    scored: list[tuple[int, int, Passage]] = []
    order = 0
    for section in sections_of(material_text):
        for number, paragraph in enumerate(section.paragraphs, start=1):
            for sentence in text.sentences(paragraph):
                overlap = len(wanted & text.keywords(sentence))
                if overlap >= needed:
                    location = f"«{material_title}», {section.heading}, párrafo {number}"
                    scored.append((overlap, -order, Passage(sentence, location)))
                order += 1
    scored.sort(reverse=True)
    return [passage for _, _, passage in scored[:MAX_PASSAGES]]


def most_relevant_section(task: str, material_text: str) -> Section | None:
    """The section whose words overlap the most with the task; the first one on a tie or none."""
    sections = sections_of(material_text)
    if not sections:
        return None
    wanted = text.keywords(task)

    def score(section: Section) -> int:
        words = text.keywords(section.heading + " " + " ".join(section.paragraphs))
        return len(wanted & words)

    best = max(sections, key=score)
    return best if score(best) > 0 else sections[0]
