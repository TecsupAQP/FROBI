from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from fakes.materials import SAMPLE
from frobi.modules.materials.domain import (
    EmptyText,
    InvalidTitle,
    Material,
    MaterialKind,
    MaterialSource,
)

NOW = datetime(2026, 11, 5, 10, 0, tzinfo=UTC)


def _create(title: str = "Guía", text: str = "Texto", owner: UUID | None = None) -> Material:
    return Material.create(
        owner_id=owner or uuid4(),
        title=title,
        kind=MaterialKind.GUIDE,
        source=MaterialSource.PASTE,
        text=text,
        now=NOW,
    )


def test_text_keeps_paragraphs_but_drops_extra_blank_lines_and_spaces() -> None:
    material = _create(text="  Primer   párrafo \r\n\r\n\r\n\r\n Segundo  ")

    assert material.text == "Primer párrafo\n\nSegundo"


@pytest.mark.parametrize("text", ["", "   ", "\n\n \n"])
def test_empty_text_is_rejected(text: str) -> None:
    with pytest.raises(EmptyText):
        _create(text=text)


@pytest.mark.parametrize("title", ["   ", "x" * 121])
def test_title_must_have_1_to_120_characters(title: str) -> None:
    with pytest.raises(InvalidTitle):
        _create(title=title)


def test_a_material_is_only_visible_to_its_owner() -> None:
    owner = uuid4()
    material = _create(owner=owner)

    assert material.visible_to(owner)
    assert not material.visible_to(uuid4())


def test_samples_are_visible_to_everyone() -> None:
    assert SAMPLE.visible_to(uuid4())


def test_preview_is_short_and_flat() -> None:
    material = _create(text="Línea uno\n\n" + "palabra " * 100)

    preview = material.preview()

    assert "\n" not in preview
    assert len(preview) <= 160
    assert preview.endswith("…")
