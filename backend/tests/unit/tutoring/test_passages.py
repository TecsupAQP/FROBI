from frobi.modules.tutoring.domain import find_passages, most_relevant_section, sections_of

GUIDE = """## Sensores inductivos
Los sensores inductivos detectan metales sin contacto. Su distancia es corta.
## Sensores capacitivos
Los sensores capacitivos detectan plásticos y líquidos. Se usan en envasado de botellas.
## Temperatura
El termopar mide temperatura alta."""


def test_sections_follow_the_headings() -> None:
    assert [s.heading for s in sections_of(GUIDE)] == [
        "Sensores inductivos",
        "Sensores capacitivos",
        "Temperatura",
    ]


def test_an_answer_finds_the_sentences_it_talks_about_with_location() -> None:
    passages = find_passages("El capacitivo detecta la botella de plástico", "Guía", GUIDE)

    assert passages[0].text == "Los sensores capacitivos detectan plásticos y líquidos."
    assert all("Sensores capacitivos" in p.location for p in passages)
    assert passages[0].location.startswith("«Guía», Sensores capacitivos, párrafo 1")


def test_accents_and_case_do_not_matter() -> None:
    assert find_passages("LIQUIDOS y PLASTICOS", "Guía", GUIDE)


def test_an_unrelated_answer_finds_nothing() -> None:
    assert find_passages("No sé nada de esto", "Guía", GUIDE) == []


def test_at_most_three_passages() -> None:
    text = "\n".join(f"Los sensores detectan metales número {n}." for n in range(10))

    assert len(find_passages("sensores detectan metales", "Guía", text)) == 3


def test_most_relevant_section_for_a_task() -> None:
    section = most_relevant_section("¿Qué sensor detecta una botella de plástico?", GUIDE)

    assert section is not None
    assert section.heading == "Sensores capacitivos"


def test_a_task_without_keywords_points_to_the_first_section() -> None:
    section = most_relevant_section("ejercicio-1", GUIDE)

    assert section is not None
    assert section.heading == "Sensores inductivos"
