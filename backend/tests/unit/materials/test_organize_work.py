from frobi.modules.materials.domain import organize

BRIEF = """Informe final de Instrumentación
1. Explicar qué es un sensor y qué señal entrega.
2. Comparar sensores inductivos y capacitivos.
3. Dar un ejemplo industrial de selección de sensores.
- Incluir una conclusión personal.
"""

DRAFT = """# Introducción
Un sensor convierte una magnitud física en una señal eléctrica.

# Inductivos y capacitivos
Los sensores inductivos detectan metales. Los capacitivos detectan plásticos y líquidos.
"""


def test_numbered_and_bulleted_lines_become_requirements() -> None:
    result = organize(BRIEF, DRAFT)

    assert result.requirements == (
        "Explicar qué es un sensor y qué señal entrega",
        "Comparar sensores inductivos y capacitivos",
        "Dar un ejemplo industrial de selección de sensores",
        "Incluir una conclusión personal",
    )


def test_headings_of_the_draft_become_topics() -> None:
    assert organize(BRIEF, DRAFT).topics == ("Introducción", "Inductivos y capacitivos")


def test_requirements_the_draft_does_not_touch_are_missing() -> None:
    assert organize(BRIEF, DRAFT).missing == (
        "Dar un ejemplo industrial de selección de sensores",
        "Incluir una conclusión personal",
    )


def test_matching_ignores_accents_and_case() -> None:
    result = organize("- Hablar de la CONCLUSIÓN", "Mi conclusion es que funciona.")

    assert result.missing == ()


def test_a_brief_without_bullets_is_split_into_sentences() -> None:
    result = organize(
        "Describe los sensores ópticos. Indica dónde se usan en una planta.",
        "Sensores ópticos en la planta de envasado.",
    )

    assert result.requirements == (
        "Describe los sensores ópticos",
        "Indica dónde se usan en una planta",
    )
    assert result.missing == ()


def test_a_draft_without_headings_uses_the_start_of_each_paragraph() -> None:
    result = organize(
        "- Algo", "Primera idea del texto. Sigue.\nSegunda idea larga del párrafo aquí."
    )

    assert result.topics == ("Primera idea del texto", "Segunda idea larga del párrafo aquí")
