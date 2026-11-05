"""Shared AI engine plumbing (PLAN_BACKEND §7).

Modules never see this from their use cases: each module defines its own port (TextGenerator,
HintGenerator, …) and its LLM adapter uses these pieces:

- ``LlmClient``: the provider. ``DisabledLlmClient`` until a provider is chosen.
- ``call_with_fallback``: 15 s cap; on timeout, error or invalid output, use the fallback.
- ``RedisRateLimiter``: ``ratelimit:ai:{person_id}`` per minute, to protect the provider quota.
- ``SYSTEM_PROMPT``: the fixed engine rule (only the loaded material; say when something is
  not there).
"""

from .client import DisabledLlmClient, LlmClient, LlmUnavailable
from .fallback import call_with_fallback
from .prompts import SYSTEM_PROMPT
from .rate_limit import AllowAll, RateLimiter, RedisRateLimiter

__all__ = [
    "SYSTEM_PROMPT",
    "AllowAll",
    "DisabledLlmClient",
    "LlmClient",
    "LlmUnavailable",
    "RateLimiter",
    "RedisRateLimiter",
    "call_with_fallback",
]
