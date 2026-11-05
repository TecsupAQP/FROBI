import pytest

from frobi.modules.adaptations.domain import (
    ENGINE_RULE,
    AdaptedContent,
    Format,
    Recipe,
    Section,
    cache_key,
    suggested_format,
)


def test_recipe_has_the_four_pieces_and_the_engine_rule() -> None:
    recipe = Recipe.build(material_title="Guía", fmt=Format.EASY_READ, enabled_settings=[])

    text = recipe.prompt_text()

    assert "Contexto: Estudio el material «Guía»." in text
    for piece in ("Objetivo:", "Nivel:", "Formato:"):
        assert piece in text
    assert "lectura fácil" in text
    assert text.endswith(ENGINE_RULE)


def test_short_texts_setting_lowers_the_level() -> None:
    simple = Recipe.build(material_title="G", fmt=Format.AUDIO, enabled_settings=["short_texts"])
    normal = Recipe.build(material_title="G", fmt=Format.AUDIO, enabled_settings=[])

    assert "frases cortas" in simple.level
    assert simple.level != normal.level


def test_cache_key_depends_on_text_format_and_profile_not_on_order() -> None:
    base = cache_key("texto", Format.AUDIO, ["voice", "captions"])

    assert base == cache_key("texto", Format.AUDIO, ["captions", "voice"])
    assert base != cache_key("texto", Format.EASY_READ, ["voice", "captions"])
    assert base != cache_key("texto", Format.AUDIO, ["voice"])
    assert base != cache_key("otro texto", Format.AUDIO, ["voice", "captions"])


@pytest.mark.parametrize(
    ("enabled", "expected"),
    [
        (["voice", "short_texts"], Format.AUDIO),
        (["short_texts"], Format.EASY_READ),
        (["captions"], Format.VISUAL_MAP),
        (["keyboard_mode"], Format.REAL_EXAMPLE),
        ([], None),
    ],
)
def test_suggested_format_follows_the_profile(enabled: list[str], expected: Format | None) -> None:
    assert suggested_format(enabled) is expected


def test_plain_text_reads_title_sections_and_items_in_order() -> None:
    content = AdaptedContent(
        title="Sensores",
        sections=(Section("Tipos", "Hay dos.", ("Inductivo", "Capacitivo.")),),
    )

    assert content.plain_text() == "Sensores. Tipos. Hay dos. Inductivo. Capacitivo."
