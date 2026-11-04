import asyncio

from frobi.shared.application import check_health


class Probe:
    def __init__(self, name: str, *, fails: bool = False, delay: float = 0.0) -> None:
        self.name = name
        self._fails = fails
        self._delay = delay

    async def check(self) -> None:
        await asyncio.sleep(self._delay)
        if self._fails:
            raise ConnectionError(self.name)


async def test_every_probe_that_answers_is_up() -> None:
    result = await check_health([Probe("postgres"), Probe("redis")], timeout_seconds=1)

    assert result == {"postgres": True, "redis": True}


async def test_a_probe_that_raises_is_down_without_affecting_others() -> None:
    result = await check_health([Probe("postgres", fails=True), Probe("redis")], timeout_seconds=1)

    assert result == {"postgres": False, "redis": True}


async def test_a_probe_slower_than_the_timeout_is_down() -> None:
    result = await check_health([Probe("redis", delay=1)], timeout_seconds=0.01)

    assert result == {"redis": False}
