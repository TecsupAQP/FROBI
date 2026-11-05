"""The traffic light without AI, including the scripted demo case (PLAN_BACKEND M9)."""

from uuid import uuid4

import pytest

from fakes.adaptations import Limiter, ScriptedLlm
from frobi.modules.claim_review.domain import (
    ClaimInput,
    ClaimStatus,
    claims_of,
    judge,
    passages_of,
)
from frobi.modules.claim_review.infrastructure import (
    LlmReviewer,
    ResilientReviewer,
    RuleBasedReviewer,
)

GUIDE = """## Sensores inductivos
Los sensores inductivos detectan metales sin contacto. Su distancia de detección es de unos 4 mm.
## Sensores capacitivos
Los sensores capacitivos detectan metales y también plásticos y líquidos no metálicos.
## Temperatura
El termopar no necesita alimentación externa para medir temperatura."""
PASSAGES = passages_of([GUIDE])

DEMO_DRAFT = """# Introducción
Los sensores inductivos detectan metales sin contacto.
Los sensores capacitivos solo detectan metales.
# Conclusión
Los sensores ópticos son los más baratos del mercado.
¿Qué sensor conviene usar en cada caso?"""


def test_claims_are_the_affirmative_sentences_grouped_by_section() -> None:
    claims = claims_of(DEMO_DRAFT)

    assert [(c.section, c.fragment) for c in claims] == [
        ("Introducción", "Los sensores inductivos detectan metales sin contacto."),
        ("Introducción", "Los sensores capacitivos solo detectan metales."),
        ("Conclusión", "Los sensores ópticos son los más baratos del mercado."),
    ]


def test_headings_are_not_passages() -> None:
    assert not any(p.startswith("#") or p == "Sensores inductivos" for p in PASSAGES)


def test_the_scripted_demo_gives_the_three_colours() -> None:
    supported, contradicts, unverifiable = (
        judge(c.fragment, PASSAGES) for c in claims_of(DEMO_DRAFT)
    )

    assert supported.status is ClaimStatus.SUPPORTED
    assert supported.backing_passage == "Los sensores inductivos detectan metales sin contacto."
    assert contradicts.status is ClaimStatus.CONTRADICTS
    assert contradicts.reason == "Tu material dice que no es solo eso."
    assert contradicts.backing_passage is not None
    assert "también" in contradicts.backing_passage
    assert unverifiable.status is ClaimStatus.UNVERIFIABLE
    assert unverifiable.backing_passage is None


def test_a_different_number_contradicts() -> None:
    verdict = judge("La distancia de detección de los sensores inductivos es de 40 mm.", PASSAGES)

    assert verdict.status is ClaimStatus.CONTRADICTS
    assert verdict.reason == "Los números no coinciden con tu material."


def test_a_negation_on_a_shared_idea_contradicts() -> None:
    verdict = judge("Los sensores inductivos no detectan metales.", PASSAGES)

    assert verdict.status is ClaimStatus.CONTRADICTS
    assert verdict.reason == "Tu material dice lo contrario."


def test_an_unrelated_no_in_the_passage_is_not_a_contradiction() -> None:
    verdict = judge("Los sensores capacitivos detectan plásticos y líquidos.", PASSAGES)

    assert verdict.status is ClaimStatus.SUPPORTED


SAMPLE_GUIDE_EXCERPT = passages_of(
    [
        "## Sensores fotoeléctricos\n"
        "Los sensores fotoeléctricos usan un haz de luz. Alcanzan distancias mayores que los "
        "inductivos, pero el polvo o el vapor pueden afectarlos.\n"
        "## Temperatura\n"
        "La RTD mide temperatura por el cambio de resistencia de un metal; es más precisa que el "
        "termopar, pero trabaja en rangos más bajos."
    ]
)


def test_denying_what_the_material_affirms_contradicts_across_word_forms() -> None:
    verdict = judge(
        "Los sensores fotoeléctricos no se ven afectados por el polvo.", SAMPLE_GUIDE_EXCERPT
    )

    assert verdict.status is ClaimStatus.CONTRADICTS
    assert verdict.backing_passage is not None
    assert "polvo" in verdict.backing_passage


def test_an_inverted_comparison_contradicts() -> None:
    verdict = judge("El termopar es más preciso que la RTD.", SAMPLE_GUIDE_EXCERPT)

    assert verdict.status is ClaimStatus.CONTRADICTS
    assert verdict.reason == "Tu material compara al revés."


def test_the_same_comparison_is_supported() -> None:
    verdict = judge("La RTD es más precisa que el termopar.", SAMPLE_GUIDE_EXCERPT)

    assert verdict.status is ClaimStatus.SUPPORTED


def test_the_closed_vocabulary_has_no_false() -> None:
    assert {s.value for s in ClaimStatus} == {"supported", "unverifiable", "contradicts"}


CLAIMS = [ClaimInput("Intro", "Los sensores inductivos detectan metales sin contacto.")]


def _resilient(llm: ScriptedLlm, timeout: float = 1.0) -> ResilientReviewer:
    return ResilientReviewer(LlmReviewer(llm), RuleBasedReviewer(), Limiter(True), timeout)


async def test_an_ai_verdict_with_a_real_passage_is_kept() -> None:
    llm = ScriptedLlm(
        reply={
            "verdicts": [
                {
                    "status": "supported",
                    "reason": "Coincide con la guía.",
                    "backing_passage": "Los sensores inductivos detectan metales sin contacto.",
                }
            ]
        }
    )

    [verdict] = await _resilient(llm).review(requested_by=uuid4(), claims=CLAIMS, guides=[GUIDE])

    assert verdict.reason == "Coincide con la guía."
    assert verdict.status is ClaimStatus.SUPPORTED


async def test_an_ai_passage_that_is_not_in_the_material_is_treated_as_invented() -> None:
    llm = ScriptedLlm(
        reply={
            "verdicts": [
                {
                    "status": "supported",
                    "reason": "x",
                    "backing_passage": "Los inductivos fueron inventados en 1958.",
                }
            ]
        }
    )

    [verdict] = await _resilient(llm).review(requested_by=uuid4(), claims=CLAIMS, guides=[GUIDE])

    assert verdict.status is ClaimStatus.UNVERIFIABLE
    assert verdict.backing_passage is None


@pytest.mark.parametrize(
    "llm",
    [
        ScriptedLlm(reply={"verdicts": []}),
        ScriptedLlm(reply={"verdicts": [{"status": "false", "reason": "x"}]}),
        ScriptedLlm(reply={"verdicts": [{"status": "supported", "reason": "x"}]}, delay=2),
    ],
    ids=["wrong-count", "forbidden-status", "slow"],
)
async def test_bad_or_slow_ai_reviews_fall_back_to_the_rules(llm: ScriptedLlm) -> None:
    [verdict] = await _resilient(llm, timeout=0.05).review(
        requested_by=uuid4(), claims=CLAIMS, guides=[GUIDE]
    )

    assert verdict.status is ClaimStatus.SUPPORTED
    assert verdict.reason == "Tu material dice lo mismo."
