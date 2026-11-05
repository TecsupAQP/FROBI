"""pypdf reads the outline and the font sizes of real PDFs."""

from frobi.modules.materials.infrastructure import PypdfTextExtractor
from pdf import make_structured_pdf

BODY = [("El sensor inductivo detecta metales sin contacto en la linea.", 11)] * 3


async def test_lines_in_a_bigger_font_are_headings() -> None:
    pdf = make_structured_pdf([[("Sensores inductivos", 22), *BODY], [("Capacitivos", 22), *BODY]])

    content = await PypdfTextExtractor().extract(pdf)

    assert content.headings == ((0, "Sensores inductivos"), (1, "Capacitivos"))
    assert len(content.pages) == 2


async def test_bookmarks_become_the_outline() -> None:
    pdf = make_structured_pdf([BODY, BODY, BODY], outline=[("Unidad 1", 0), ("Unidad 2", 2)])

    content = await PypdfTextExtractor().extract(pdf)

    assert [(e.title, e.page, e.level) for e in content.outline] == [
        ("Unidad 1", 0, 0),
        ("Unidad 2", 2, 0),
    ]
    assert content.headings == ()
