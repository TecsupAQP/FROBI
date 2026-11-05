"""Claim verdicts: the model first (15 s cap), text-matching rules otherwise.

The model's answer is checked against the material: a backing passage that does not appear in
the person's guides is treated as invented, and that claim becomes «unverifiable».
"""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.claim_review.domain import (
    REASONS,
    ClaimInput,
    ClaimStatus,
    Verdict,
    judge,
    passages_of,
)
from frobi.shared.domain import text
from frobi.shared.infrastructure.llm import (
    SYSTEM_PROMPT,
    LlmClient,
    RateLimiter,
    call_with_fallback,
)

MAX_GUIDE_CHARS = 20_000


class RuleBasedReviewer:
    async def review(
        self, *, requested_by: UUID, claims: list[ClaimInput], guides: list[str]
    ) -> list[Verdict]:
        passages = passages_of(guides)
        return [judge(claim.fragment, passages) for claim in claims]


class _VerdictJson(BaseModel):
    status: ClaimStatus
    reason: str = Field(min_length=1, max_length=400)
    backing_passage: str | None = Field(default=None, max_length=2000)


class _ReviewJson(BaseModel):
    verdicts: list[_VerdictJson]


def _appears_in(passage: str, guides: list[str]) -> bool:
    needle = " ".join(text.fold(passage).split())
    return any(needle in " ".join(text.fold(g).split()) for g in guides)


class LlmReviewer:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def review(
        self, *, requested_by: UUID, claims: list[ClaimInput], guides: list[str]
    ) -> list[Verdict]:
        numbered = "\n".join(f"{i + 1}. {c.fragment}" for i, c in enumerate(claims))
        material = "\n\n".join(guides)[:MAX_GUIDE_CHARS]
        data = await self._llm.complete_json(
            system=SYSTEM_PROMPT,
            prompt=(
                "Para cada afirmación del borrador di si el material la respalda (supported), "
                "no habla de ella (unverifiable) o dice lo contrario (contradicts). Nunca digas "
                "«falso» ni estimes si lo escribió una IA. Si hay respaldo o contradicción, copia "
                "textual el pasaje del material.\n\n"
                f"Afirmaciones:\n{numbered}\n\nMaterial:\n<<<\n{material}\n>>>\n\n"
                'Responde con este JSON: {"verdicts": [{"status": str, "reason": str, '
                '"backing_passage": str | null}]} en el mismo orden.'
            ),
        )
        parsed = _ReviewJson.model_validate(data)
        if len(parsed.verdicts) != len(claims):
            raise ValueError("One verdict per claim is required")
        verdicts = []
        for v in parsed.verdicts:
            passage = v.backing_passage.strip() if v.backing_passage else None
            if v.status is ClaimStatus.UNVERIFIABLE or not passage:
                verdicts.append(Verdict(ClaimStatus.UNVERIFIABLE, v.reason, None))
            elif not _appears_in(passage, guides):
                verdicts.append(Verdict(ClaimStatus.UNVERIFIABLE, REASONS["absent"], None))
            else:
                verdicts.append(Verdict(v.status, v.reason, passage))
        return verdicts


class ResilientReviewer:
    def __init__(
        self,
        primary: LlmReviewer,
        fallback: RuleBasedReviewer,
        limiter: RateLimiter,
        timeout_seconds: float,
    ) -> None:
        self._primary, self._fallback = primary, fallback
        self._limiter, self._timeout = limiter, timeout_seconds

    async def review(
        self, *, requested_by: UUID, claims: list[ClaimInput], guides: list[str]
    ) -> list[Verdict]:
        result, _ = await call_with_fallback(
            lambda: self._primary.review(requested_by=requested_by, claims=claims, guides=guides),
            lambda: self._fallback.review(requested_by=requested_by, claims=claims, guides=guides),
            timeout_seconds=self._timeout,
            allowed=await self._limiter.allow(requested_by),
        )
        return result


__all__ = ["LlmReviewer", "ResilientReviewer", "RuleBasedReviewer"]
