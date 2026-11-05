"""The cheapest source of topics that works: outline, fonts, text headings, then the AI."""

from uuid import uuid4

from fakes.identity import FakeUnitOfWork, FixedClock
from fakes.materials import FakeExtractor, InMemoryMaterials, ScriptedSegmenter
from frobi.modules.materials.application import (
    TopicFinder,
    UploadMaterialCommand,
    UploadMaterialHandler,
)
from frobi.modules.materials.application.ports import OutlineEntry
from frobi.modules.materials.domain import MAX_TOPIC_CHARS, MaterialKind, assemble_pages

PARAGRAPH = "Los sensores detectan cambios en el entorno y los convierten en señales. " * 6
LONG_PLAIN = "\n\n".join(f"Idea {n}. {PARAGRAPH}" for n in range(30))


async def test_the_pdf_outline_comes_first() -> None:
    text, offsets = assemble_pages([PARAGRAPH, f"Sensores\n{PARAGRAPH}", PARAGRAPH])
    outline = [OutlineEntry("Introducción", 0, 0), OutlineEntry("Sensores", 1, 0)]
    segmenter = ScriptedSegmenter([(0, "No se usa")])

    spans = await TopicFinder(segmenter).find("Guía", text, page_offsets=offsets, outline=outline)

    assert [(s.title, s.page_start, s.page_end) for s in spans] == [
        ("Introducción", 1, 1),
        ("Sensores", 2, 3),
    ]
    assert segmenter.blocks == []  # the AI was never asked


async def test_bigger_fonts_come_next() -> None:
    text, offsets = assemble_pages([f"Inductivos\n{PARAGRAPH}", f"Capacitivos\n{PARAGRAPH}"])

    spans = await TopicFinder().find(
        "Guía", text, page_offsets=offsets, headings=[(0, "Inductivos"), (1, "Capacitivos")]
    )

    assert [s.title for s in spans] == ["Inductivos", "Capacitivos"]


async def test_the_ai_reads_only_the_skeleton_of_a_long_plain_text() -> None:
    segmenter = ScriptedSegmenter([(0, "Primeras ideas"), (15, "Últimas ideas")])

    spans = await TopicFinder(segmenter).find("Guía", LONG_PLAIN)

    assert len(segmenter.blocks) == 30
    assert all(len(block) <= 90 for block in segmenter.blocks)
    assert sum(len(b) for b in segmenter.blocks) < len(LONG_PLAIN) / 4
    titles = [s.title for s in spans]
    assert titles[0].startswith("Primeras ideas")
    assert any(title.startswith("Últimas ideas") for title in titles)
    assert all(s.end - s.start <= MAX_TOPIC_CHARS for s in spans)


async def test_without_the_ai_long_text_is_cut_by_size() -> None:
    spans = await TopicFinder(ScriptedSegmenter(None)).find("Guía", LONG_PLAIN)

    assert len(spans) > 1
    assert spans[0].title.startswith("Parte 1:")


async def test_short_plain_text_never_calls_the_ai() -> None:
    segmenter = ScriptedSegmenter([(0, "x"), (1, "y")])

    spans = await TopicFinder(segmenter).find("Guía", PARAGRAPH)

    assert [s.title for s in spans] == ["Todo el material"]
    assert segmenter.blocks == []


async def test_an_uploaded_pdf_keeps_its_topics_and_pages() -> None:
    materials = InMemoryMaterials()
    pages = "\f".join([f"Inductivos\n{PARAGRAPH}", PARAGRAPH, f"Capacitivos\n{PARAGRAPH}"])
    extractor = FakeExtractor(
        outline=(OutlineEntry("Inductivos", 0, 0), OutlineEntry("Capacitivos", 2, 0))
    )
    handler = UploadMaterialHandler(FakeUnitOfWork(), materials, extractor, FixedClock())

    material = await handler.handle(
        UploadMaterialCommand(
            owner_id=uuid4(), title="Sensores", kind=MaterialKind.GUIDE, data=pages.encode()
        )
    )

    topics = materials.items[material.id].topics()
    assert [(t.position, t.title, t.page_start, t.page_end) for t in topics] == [
        (1, "Inductivos", 1, 2),
        (2, "Capacitivos", 3, 3),
    ]
    assert topics[1].text.startswith("Capacitivos")
