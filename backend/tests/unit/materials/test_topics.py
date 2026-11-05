"""Topics: found from the text's own headings and always of a size the AI takes in one go."""

from frobi.modules.materials.domain import (
    MAX_TOPIC_CHARS,
    MIN_TOPIC_CHARS,
    Boundary,
    assemble_pages,
    normalize_text,
    spans_from_boundaries,
    text_heading_boundaries,
)
from frobi.modules.materials.domain.topics import MAX_TOPICS, topics_of

PARAGRAPH = "Los sensores detectan cambios en el entorno y los convierten en señales. " * 6


def _topics(text: str) -> list[tuple[str, str]]:
    spans = spans_from_boundaries(text, text_heading_boundaries(text))
    return [(t.title, t.text) for t in topics_of(text, spans)]


def test_markdown_headings_make_topics() -> None:
    text = f"## Inductivos\n{PARAGRAPH}\n\n## Capacitivos\n{PARAGRAPH}"

    assert [title for title, _ in _topics(text)] == ["Inductivos", "Capacitivos"]


def test_unit_and_chapter_headings_make_topics() -> None:
    text = f"Unidad 1: Sensores\n{PARAGRAPH}\n\nUnidad 2: Actuadores\n{PARAGRAPH}"

    assert [title for title, _ in _topics(text)] == ["Unidad 1: Sensores", "Unidad 2: Actuadores"]


def test_a_numbered_list_is_not_a_set_of_topics() -> None:
    steps = "\n\n".join(f"{n}. Conecta el cable {n}" for n in range(1, 6))
    text = f"Instalación\n\n{steps}\n\n{PARAGRAPH}"

    assert [title for title, _ in _topics(text)] == ["Todo el material"]


def test_spaced_numbered_headings_are_topics() -> None:
    text = "\n\n".join(f"{n} Tema número {n}\n\n{PARAGRAPH * 2}" for n in range(1, 4))

    assert [title for title, _ in _topics(text)] == [f"{n} Tema número {n}" for n in range(1, 4)]


def test_a_short_text_without_headings_is_one_topic() -> None:
    assert _topics(PARAGRAPH) == [("Todo el material", PARAGRAPH.strip())]


def test_a_long_text_without_headings_is_cut_into_named_parts() -> None:
    text = "\n\n".join(f"Idea {n}. {PARAGRAPH}" for n in range(40))

    topics = _topics(text)

    assert len(topics) > 1
    assert all(len(body) <= MAX_TOPIC_CHARS for _, body in topics)
    assert topics[0][0].startswith("Parte 1: Idea 0")
    # Cut at paragraph breaks: no idea is split in two.
    assert all(body.startswith("Idea") for _, body in topics)


def test_a_long_topic_is_split_into_parts() -> None:
    long = "\n\n".join([PARAGRAPH] * 20)
    text = f"## Inductivos\n{long}\n\n## Capacitivos\n{PARAGRAPH}"

    titles = [title for title, _ in _topics(text)]

    assert titles[0] == "Inductivos (parte 1)"
    assert titles[1] == "Inductivos (parte 2)"
    assert titles[-1] == "Capacitivos"


def test_tiny_topics_join_the_previous_one() -> None:
    text = f"## Inductivos\n{PARAGRAPH}\n\n## Nota\nBreve.\n\n## Capacitivos\n{PARAGRAPH}"

    topics = _topics(text)

    assert [title for title, _ in topics] == ["Inductivos", "Capacitivos"]
    assert "Breve." in topics[0][1]


def test_a_long_preamble_becomes_an_introduction() -> None:
    text = f"{PARAGRAPH}\n\n## Inductivos\n{PARAGRAPH}\n\n## Capacitivos\n{PARAGRAPH}"

    assert [title for title, _ in _topics(text)] == ["Introducción", "Inductivos", "Capacitivos"]


def test_topics_know_their_pages() -> None:
    text, offsets = assemble_pages([f"## A\n{PARAGRAPH}", PARAGRAPH, f"## B\n{PARAGRAPH}"])

    spans = spans_from_boundaries(text, text_heading_boundaries(text), offsets)

    assert [(s.title, s.page_start, s.page_end) for s in spans] == [("A", 1, 2), ("B", 3, 3)]


def test_assembled_pages_are_already_normal_text() -> None:
    text, offsets = assemble_pages(["  Página   uno \n\n\n más ", "", "Página tres"])

    assert normalize_text(text) == text
    assert text[offsets[0] :].startswith("Página uno")
    assert text[offsets[2] :] == "Página tres"


def test_there_is_a_cap_on_the_number_of_topics() -> None:
    small = "x" * MIN_TOPIC_CHARS
    text = "\n\n".join(f"## T{n}\n{small}" for n in range(MAX_TOPICS * 2))
    boundaries = [Boundary(text.index(f"## T{n}\n"), f"T{n}") for n in range(MAX_TOPICS * 2)]

    assert len(spans_from_boundaries(text, boundaries)) <= MAX_TOPICS
