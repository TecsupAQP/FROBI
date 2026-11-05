"""Adapt a material to a format with the 4-piece recipe (RF04, RF05, RF07, RF29, RF30).

Same text + format + profile is served from the 24 h cache so the provider is not paid twice;
a lock stops a double click from generating the same thing in parallel. Fallback results are
not cached, so the next try can still get the AI version.
"""

import asyncio

from frobi.modules.adaptations.application.ports import (
    AdaptationCache,
    AdaptationRepository,
    MaterialReader,
    ProfileReader,
    TextGenerator,
)
from frobi.modules.adaptations.domain import (
    Adaptation,
    AdaptedContent,
    MaterialNotAvailable,
    Recipe,
    cache_key,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

from .command import CreateAdaptationCommand


class CreateAdaptationHandler:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        adaptations: AdaptationRepository,
        materials: MaterialReader,
        profiles: ProfileReader,
        generator: TextGenerator,
        cache: AdaptationCache,
        clock: Clock,
        lock_wait_seconds: float = 16.0,
        lock_poll_seconds: float = 0.25,
    ) -> None:
        self._uow = uow
        self._adaptations = adaptations
        self._materials = materials
        self._profiles = profiles
        self._generator = generator
        self._cache = cache
        self._clock = clock
        self._lock_wait = lock_wait_seconds
        self._lock_poll = lock_poll_seconds

    async def handle(self, command: CreateAdaptationCommand) -> Adaptation:
        material = await self._materials.find(command.person_id, command.material_id)
        if material is None:
            raise MaterialNotAvailable()
        profile = await self._profiles.for_person(command.person_id)
        recipe = Recipe.build(
            material_title=material.title,
            fmt=command.format,
            enabled_settings=profile.enabled_settings,
        )
        key = cache_key(material.text, command.format, profile.enabled_settings)

        content = await self._cache.get(key)
        fallback = False
        if content is None:
            locked = await self._cache.try_lock(key)
            if not locked:
                content = await self._wait_for(key)
            if content is None:
                try:
                    generated = await self._generator.adapt(
                        requested_by=command.person_id, material=material, recipe=recipe
                    )
                finally:
                    if locked:
                        await self._cache.unlock(key)
                content, fallback = generated.content, generated.fallback
                if not fallback:
                    await self._cache.put(key, content)

        adaptation = Adaptation.create(
            material_id=material.id,
            person_id=command.person_id,
            class_id=command.class_id,
            content=content,
            recipe=recipe,
            fallback=fallback,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._adaptations.add(adaptation)
            await self._uow.commit()
        return adaptation

    async def _wait_for(self, key: str) -> AdaptedContent | None:
        """Someone else is generating the same adaptation: wait for their result."""
        waited = 0.0
        while waited < self._lock_wait:
            await asyncio.sleep(self._lock_poll)
            waited += self._lock_poll
            content = await self._cache.get(key)
            if content is not None:
                return content
        return None
