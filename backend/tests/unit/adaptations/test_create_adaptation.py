import asyncio
from uuid import uuid4

import pytest

from fakes.adaptations import (
    AI_CONTENT,
    SOURCE,
    CountingGenerator,
    InMemoryAdaptations,
    InMemoryCache,
    StaticMaterials,
    StaticProfiles,
)
from fakes.identity import FakeUnitOfWork, FixedClock
from frobi.modules.adaptations.application import (
    CreateAdaptationCommand,
    CreateAdaptationHandler,
    GetAdaptationHandler,
    ListFormatsHandler,
)
from frobi.modules.adaptations.domain import (
    AdaptationNotFound,
    Format,
    MaterialNotAvailable,
    cache_key,
)

ANA = uuid4()
CLASS_ID = uuid4()


def _handler(
    generator: CountingGenerator,
    cache: InMemoryCache,
    repo: InMemoryAdaptations | None = None,
    **kwargs: float,
) -> CreateAdaptationHandler:
    return CreateAdaptationHandler(
        uow=FakeUnitOfWork(),
        adaptations=repo or InMemoryAdaptations(),
        materials=StaticMaterials(owner=ANA),
        profiles=StaticProfiles("short_texts"),
        generator=generator,
        cache=cache,
        clock=FixedClock(),
        **kwargs,
    )


def _command(fmt: Format = Format.EASY_READ) -> CreateAdaptationCommand:
    return CreateAdaptationCommand(
        person_id=ANA, class_id=CLASS_ID, material_id=SOURCE.id, format=fmt
    )


async def test_adaptation_is_stored_with_recipe_and_class() -> None:
    repo = InMemoryAdaptations()

    adaptation = await _handler(CountingGenerator(), InMemoryCache(), repo).handle(_command())

    assert repo.items[adaptation.id] == adaptation
    assert adaptation.class_id == CLASS_ID
    assert adaptation.content == AI_CONTENT
    assert adaptation.recipe.format is Format.EASY_READ
    assert "frases cortas" in adaptation.recipe.level
    assert adaptation.fallback is False


async def test_someone_elses_material_cannot_be_adapted() -> None:
    handler = _handler(CountingGenerator(), InMemoryCache())

    with pytest.raises(MaterialNotAvailable):
        await handler.handle(
            CreateAdaptationCommand(
                person_id=uuid4(), class_id=None, material_id=SOURCE.id, format=Format.AUDIO
            )
        )


async def test_same_material_format_and_profile_is_served_from_cache() -> None:
    generator, cache = CountingGenerator(), InMemoryCache()
    handler = _handler(generator, cache)

    first = await handler.handle(_command())
    second = await handler.handle(_command())

    assert generator.calls == 1
    assert first.id != second.id
    assert second.content == first.content
    assert cache.locks == set()


async def test_a_different_format_is_generated_again() -> None:
    generator = CountingGenerator()
    handler = _handler(generator, InMemoryCache())

    await handler.handle(_command(Format.EASY_READ))
    await handler.handle(_command(Format.AUDIO))

    assert generator.calls == 2


async def test_fallback_answers_are_not_cached() -> None:
    generator, cache = CountingGenerator(fallback=True), InMemoryCache()
    handler = _handler(generator, cache)

    first = await handler.handle(_command())
    await handler.handle(_command())

    assert first.fallback is True
    assert generator.calls == 2
    assert cache.values == {}


async def test_a_double_click_waits_for_the_first_result_instead_of_generating() -> None:
    generator, cache = CountingGenerator(), InMemoryCache()
    key = cache_key(SOURCE.text, Format.EASY_READ, ["short_texts"])
    cache.locks.add(key)  # someone else is generating it

    async def first_request_finishes() -> None:
        await asyncio.sleep(0.05)
        await cache.put(key, AI_CONTENT)

    finisher = asyncio.create_task(first_request_finishes())
    adaptation = await _handler(
        generator, cache, lock_wait_seconds=1, lock_poll_seconds=0.01
    ).handle(_command())
    await finisher

    assert generator.calls == 0
    assert adaptation.content == AI_CONTENT


async def test_only_the_owner_can_see_an_adaptation_again() -> None:
    repo = InMemoryAdaptations()
    adaptation = await _handler(CountingGenerator(), InMemoryCache(), repo).handle(_command())
    reader = GetAdaptationHandler(repo)

    assert await reader.handle(ANA, adaptation.id) == adaptation
    with pytest.raises(AdaptationNotFound):
        await reader.handle(uuid4(), adaptation.id)


async def test_formats_mark_the_one_suggested_by_the_profile() -> None:
    options = await ListFormatsHandler(StaticProfiles("short_texts")).handle(ANA)

    assert [o.info.id for o in options] == list(Format)
    assert [o.info.id for o in options if o.suggested] == [Format.EASY_READ]
