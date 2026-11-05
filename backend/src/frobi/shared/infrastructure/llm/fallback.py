"""The 15-second rule (RF04, RF29, RNF03): never leave a person waiting on the model."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


async def call_with_fallback[T](
    primary: Callable[[], Awaitable[T]],
    fallback: Callable[[], Awaitable[T]],
    *,
    timeout_seconds: float,
    allowed: bool = True,
) -> tuple[T, bool]:
    """Run ``primary`` with a time cap; on any failure return ``fallback()``.

    Returns ``(result, used_fallback)``. ``allowed=False`` (rate limit hit) skips the model.
    """
    if allowed:
        try:
            return await asyncio.wait_for(primary(), timeout_seconds), False
        except TimeoutError:
            logger.warning("AI call exceeded %.1f s; using fallback", timeout_seconds)
        except Exception as error:
            logger.info("AI call failed (%s); using fallback", type(error).__name__)
    return await fallback(), True
