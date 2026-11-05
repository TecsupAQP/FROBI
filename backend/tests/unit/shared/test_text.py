import pytest

from frobi.shared.domain import text


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("sensores", "sensor"),
        ("metales", "metal"),
        ("plasticos", "plastico"),
        ("botellas", "botella"),
        ("liquidos", "liquido"),
        ("sensor", "sensor"),
        ("mas", "mas"),
    ],
)
def test_singular(word: str, expected: str) -> None:
    assert text.singular(word) == expected


def test_keywords_ignore_accents_case_plurals_and_filler() -> None:
    assert text.keywords("Los PLÁSTICOS y las botellas, para siempre") == {"plastico", "botella"}


def test_singular_and_plural_match_each_other() -> None:
    assert text.keywords("botella de plástico") == text.keywords("botellas de plásticos")
