"""Readiness checks for the services the API depends on."""

import asyncio
from collections.abc import Sequence
from typing import Protocol


class HealthProbe(Protocol):
    @property
    def name(self) -> str: ...

    async def check(self) -> None:
        """Return normally when the dependency answers; raise otherwise."""
        ...


async def check_health(probes: Sequence[HealthProbe], timeout_seconds: float) -> dict[str, bool]:
    """Run every probe concurrently. A probe that raises or exceeds the timeout counts as down."""

    async def run(probe: HealthProbe) -> bool:
        try:
            await asyncio.wait_for(probe.check(), timeout_seconds)
        except Exception:
            return False
        return True

    results = await asyncio.gather(*(run(probe) for probe in probes))
    return {probe.name: ok for probe, ok in zip(probes, results, strict=True)}
