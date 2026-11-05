import pytest

from frobi.modules.prompt_coach.domain import RecipePiece, autonomy_for, improve, score_prompt

C, G, L, F = RecipePiece

VAGUE = "explicame sensores"
COMPLETE = (
    "Soy estudiante de primer año de Mecatrónica y estoy leyendo la guía de sensores. "
    "Explícame la diferencia entre inductivos y capacitivos para poder preparar mi examen. "
    "No sé nada del tema, usa palabras simples. Respóndeme en una tabla de 2 columnas."
)


def test_a_vague_prompt_only_has_a_bit_of_goal() -> None:
    scores = score_prompt(VAGUE)

    assert scores == {C: 0, G: 2, L: 0, F: 0}
    assert autonomy_for(sum(scores.values())) == 1


def test_a_complete_recipe_scores_high_on_every_piece() -> None:
    scores = score_prompt(COMPLETE)

    assert all(score >= 3 for score in scores.values()), scores
    assert autonomy_for(sum(scores.values())) == 3


@pytest.mark.parametrize(
    ("prompt", "piece"),
    [
        ("Soy estudiante de química", C),
        ("Según la guía de mi clase", C),
        ("Quiero entender la presión para preparar el examen", G),
        ("Explícalo como si tuviera 12 años", L),
        ("Soy de primer año, sin conocimientos previos", L),
        ("Dámelo en 3 puntos", F),
        ("Hazlo paso a paso en una lista", F),
    ],
)
def test_each_piece_is_detected_regardless_of_accents(prompt: str, piece: RecipePiece) -> None:
    assert score_prompt(prompt)[piece] >= 2


def test_scores_never_exceed_4() -> None:
    noisy = "tabla lista esquema mapa paso a paso viñetas 5 puntos breve corto"

    assert score_prompt(noisy)[F] == 4


def test_improve_keeps_the_persons_words_and_adds_only_weak_pieces() -> None:
    improved = improve(VAGUE, score_prompt(VAGUE), "Guía de sensores")

    assert "Explicame sensores." in improved
    assert improved.startswith("Soy estudiante y estoy estudiando «Guía de sensores».")
    assert "palabras simples" in improved
    assert "3 puntos" in improved
    assert improved.endswith("Usa solo el material que te doy.")


def test_the_improved_prompt_reaches_the_highest_autonomy() -> None:
    improved = improve(VAGUE, score_prompt(VAGUE), "Guía")

    assert autonomy_for(sum(score_prompt(improved).values())) == 3


def test_a_complete_prompt_is_not_padded() -> None:
    improved = improve(COMPLETE, score_prompt(COMPLETE), None)

    assert improved == COMPLETE


@pytest.mark.parametrize(("total", "level"), [(0, 1), (6, 1), (7, 2), (11, 2), (12, 3), (16, 3)])
def test_autonomy_thresholds(total: int, level: int) -> None:
    assert autonomy_for(total) == level
