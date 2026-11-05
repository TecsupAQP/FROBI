"""The AI path, the 15 s rule and the no-AI fallbacks (no network, no database)."""

from uuid import UUID, uuid4

import pytest

from fakes.adaptations import AI_CONTENT, SOURCE, Limiter, ScriptedLlm
from frobi.modules.adaptations.application.ports import SourceMaterial
from frobi.modules.adaptations.domain import Format, Recipe
from frobi.modules.adaptations.infrastructure import (
    FallbackTextGenerator,
    LlmTextGenerator,
    ResilientTextGenerator,
    build_prompt,
    rule_based,
)
from frobi.shared.infrastructure.llm import DisabledLlmClient, LlmUnavailable

SAMPLE = SourceMaterial(id=UUID("00000000-0000-4000-8000-00000000a001"), title="Guía", text="texto")


def _recipe(fmt: Format = Format.EASY_READ) -> Recipe:
    return Recipe.build(material_title=SOURCE.title, fmt=fmt, enabled_settings=[])


def _resilient(
    llm: object, *, allowed: bool = True, timeout: float = 1.0
) -> ResilientTextGenerator:
    return ResilientTextGenerator(
        primary=LlmTextGenerator(llm),  # type: ignore[arg-type]
        fallback=FallbackTextGenerator(),
        limiter=Limiter(allowed),
        timeout_seconds=timeout,
    )


async def _adapt(generator: ResilientTextGenerator, material: SourceMaterial = SOURCE):  # type: ignore[no-untyped-def]
    return await generator.adapt(requested_by=uuid4(), material=material, recipe=_recipe())


async def test_a_valid_ai_answer_is_used() -> None:
    result = await _adapt(_resilient(ScriptedLlm()))

    assert result.fallback is False
    assert result.content == AI_CONTENT


async def test_an_ai_slower_than_the_cap_falls_back() -> None:
    llm = ScriptedLlm(delay=2)

    result = await _adapt(_resilient(llm, timeout=0.05))

    assert llm.calls == 1
    assert result.fallback is True


@pytest.mark.parametrize(
    "llm",
    [
        ScriptedLlm(reply={"title": "sin secciones"}),
        ScriptedLlm(reply={"nada": 1}),
        ScriptedLlm(error=LlmUnavailable("caído")),
        ScriptedLlm(error=RuntimeError("500")),
    ],
    ids=["no-sections", "wrong-shape", "unavailable", "provider-error"],
)
async def test_invalid_or_failed_ai_answers_fall_back(llm: ScriptedLlm) -> None:
    assert (await _adapt(_resilient(llm))).fallback is True


async def test_without_a_provider_everything_falls_back() -> None:
    assert (await _adapt(_resilient(DisabledLlmClient()))).fallback is True


async def test_over_the_rate_limit_the_model_is_not_called() -> None:
    llm = ScriptedLlm()

    result = await _adapt(_resilient(llm, allowed=False))

    assert llm.calls == 0
    assert result.fallback is True


@pytest.mark.parametrize("fmt", list(Format))
async def test_the_sample_guide_has_a_prewritten_answer_per_format(fmt: Format) -> None:
    result = await FallbackTextGenerator().adapt(
        requested_by=uuid4(), material=SAMPLE, recipe=_recipe(fmt)
    )

    assert result.fallback is True
    assert len(result.content.sections) >= 4
    assert "sensor" in result.content.plain_text().lower()


def test_rule_based_fallback_only_reorganizes_the_persons_text() -> None:
    content = rule_based(SOURCE, Format.VISUAL_MAP)

    assert content.title == SOURCE.title
    assert [s.heading for s in content.sections] == ["Inductivos", "Capacitivos"]
    assert content.sections[0].body == "Detectan metales sin contacto."


def test_rule_based_without_headings_uses_paragraphs() -> None:
    material = SourceMaterial(id=uuid4(), title="Notas", text="Primera idea.\n\nSegunda idea.")

    content = rule_based(material, Format.EASY_READ)

    assert [s.heading for s in content.sections] == ["Parte 1", "Parte 2"]


def test_rule_based_easy_read_shortens_long_sentences() -> None:
    long_sentence = " ".join(["palabra"] * 40) + "."
    material = SourceMaterial(id=uuid4(), title="Notas", text=long_sentence)

    body = rule_based(material, Format.EASY_READ).sections[0].body

    assert len(body.split()) <= 16
    assert body.endswith("…")


def test_the_prompt_sent_to_the_model_starts_with_the_visible_recipe() -> None:
    recipe = _recipe()

    prompt = build_prompt(SOURCE, recipe)

    assert prompt.startswith(recipe.prompt_text())
    assert SOURCE.text in prompt
