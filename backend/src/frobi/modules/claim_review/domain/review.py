"""Claim review (RF19, RF20): each sentence of a draft against the person's own guides.

Closed vocabulary (RNF11, RNF14): ``supported``, ``unverifiable`` or ``contradicts``. There is no
«false» and no AI-percentage: FROBI says what the material backs, not whether the person cheated.

Without AI the verdict comes from text matching:
- the guide sentence sharing the most topic words is the candidate backing passage;
- with enough overlap it backs the claim, unless a contradiction signal shows up
  («solo» vs «también», different numbers, a negation on a shared idea);
- with too little overlap the material simply does not talk about it.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from frobi.shared.domain import text

NO_BACKING = "No hay respaldo en tu material."
MAX_CLAIMS = 20
MIN_WORDS = 5
_TOKEN = re.compile(r"[a-z0-9]+")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
_NEGATIONS = frozenset({"no", "nunca", "jamas", "ningun", "ninguna", "tampoco"})
_ONLY = frozenset({"solo", "solamente", "unicamente", "exclusivamente"})
_ALSO = frozenset({"tambien", "ademas"})


class ClaimStatus(StrEnum):
    SUPPORTED = "supported"
    UNVERIFIABLE = "unverifiable"
    CONTRADICTS = "contradicts"


REASONS = {
    "same": "Tu material dice lo mismo.",
    "not_only": "Tu material dice que no es solo eso.",
    "only": "Tu material lo limita a un caso; tu frase lo amplía.",
    "numbers": "Los números no coinciden con tu material.",
    "negation": "Tu material dice lo contrario.",
    "comparison": "Tu material compara al revés.",
    "absent": "Tu material no habla de esto.",
}


@dataclass(frozen=True, slots=True)
class ClaimInput:
    section: str
    fragment: str


@dataclass(frozen=True, slots=True)
class Verdict:
    status: ClaimStatus
    reason: str
    backing_passage: str | None


def claims_of(draft_text: str) -> list[ClaimInput]:
    """Every affirmative sentence of the draft, grouped by its ``#`` section."""
    section = "Borrador"
    claims: list[ClaimInput] = []
    for line in draft_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            section = stripped.lstrip("#").strip() or section
            continue
        for sentence in text.sentences(stripped):
            if len(sentence.split()) >= MIN_WORDS and not sentence.rstrip().endswith("?"):
                claims.append(ClaimInput(section, sentence))
    return claims[:MAX_CLAIMS]


def _tokens(sentence: str) -> list[str]:
    return _TOKEN.findall(text.fold(sentence))


_ARTICLES = frozenset({"el", "la", "los", "las", "un", "una", "lo"})
NEGATION_WINDOW = 3


def _negated(tokens: list[str], shared: set[str]) -> bool:
    """A negation shortly before (≤3 words) one of the ideas both sentences talk about:
    «no se ven afectados» vs «pueden afectarlos»."""
    for i, token in enumerate(tokens):
        if token in _NEGATIONS:
            following = {text.stem(t) for t in tokens[i + 1 : i + 1 + NEGATION_WINDOW]}
            if following & shared:
                return True
    return False


def _comparisons(tokens: list[str]) -> set[tuple[str, str]]:
    """«más preciso que la RTD» → (precis, rtd)."""
    found = set()
    for i, token in enumerate(tokens[:-2]):
        if token == "mas" and tokens[i + 2] == "que":
            rest = [t for t in tokens[i + 3 :] if t not in _ARTICLES]
            if rest:
                found.add((text.stem(tokens[i + 1]), rest[0]))
    return found


def _contradiction(claim: str, passage: str, shared: set[str]) -> str | None:
    c, p = _tokens(claim), _tokens(passage)
    if _ONLY & set(c) and _ALSO & set(p):
        return "not_only"
    if _ONLY & set(p) and _ALSO & set(c):
        return "only"
    c_numbers, p_numbers = set(_NUMBER.findall(claim)), set(_NUMBER.findall(passage))
    if c_numbers and p_numbers and not c_numbers & p_numbers:
        return "numbers"
    passage_comparisons = _comparisons(p)
    for adjective, compared_with in _comparisons(c):
        if any(adj == adjective and other != compared_with for adj, other in passage_comparisons):
            return "comparison"
    if _negated(c, shared) != _negated(p, shared):
        return "negation"
    return None


MAX_BACKING_SENTENCES = 2


def best_passage(claim: str, paragraphs: list[str]) -> tuple[str | None, set[str]]:
    """The paragraph sharing the most word roots with the claim (whole paragraphs keep context:
    «los inductivos…» and «su distancia…» are read together)."""
    wanted = text.stems(claim)
    best: str | None = None
    best_shared: set[str] = set()
    for paragraph in paragraphs:
        shared = wanted & text.stems(paragraph)
        if len(shared) > len(best_shared):
            best, best_shared = paragraph, shared
    return best, best_shared


def backing_sentences(claim: str, paragraph: str) -> str:
    """Only the sentences of the paragraph that talk about the claim (at most two)."""
    wanted = text.stems(claim)
    scored = [(len(wanted & text.stems(s)), s) for s in text.sentences(paragraph)]
    relevant = [s for score, s in scored if score >= 2]
    if not relevant:
        relevant = [max(scored, key=lambda item: item[0])[1]]
    return " ".join(relevant[:MAX_BACKING_SENTENCES])


def judge(claim: str, paragraphs: list[str]) -> Verdict:
    wanted = text.stems(claim)
    paragraph, shared = best_passage(claim, paragraphs)
    related = paragraph is not None and len(shared) >= 2 and 2 * len(shared) >= len(wanted)
    if not related or paragraph is None:
        return Verdict(ClaimStatus.UNVERIFIABLE, REASONS["absent"], None)
    backing = backing_sentences(claim, paragraph)
    conflict = _contradiction(claim, backing, wanted & text.stems(backing))
    if conflict:
        return Verdict(ClaimStatus.CONTRADICTS, REASONS[conflict], backing)
    return Verdict(ClaimStatus.SUPPORTED, REASONS["same"], backing)


def passages_of(guide_texts: list[str]) -> list[str]:
    """Paragraphs of the guides, without headings."""
    return [
        line.strip()
        for guide in guide_texts
        for line in guide.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


@dataclass(frozen=True, slots=True)
class Claim:
    id: UUID
    work_id: UUID
    person_id: UUID
    class_id: UUID | None
    position: int
    section: str
    fragment: str
    status: ClaimStatus
    reason: str
    backing_passage: str | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        work_id: UUID,
        person_id: UUID,
        class_id: UUID | None,
        position: int,
        claim: ClaimInput,
        verdict: Verdict,
        now: datetime,
    ) -> "Claim":
        # Unverifiable never carries a passage, whoever produced the verdict.
        backing = None if verdict.status is ClaimStatus.UNVERIFIABLE else verdict.backing_passage
        return cls(
            id=uuid4(),
            work_id=work_id,
            person_id=person_id,
            class_id=class_id,
            position=position,
            section=claim.section,
            fragment=claim.fragment,
            status=verdict.status,
            reason=verdict.reason,
            backing_passage=backing,
            created_at=now,
        )

    @property
    def no_backing_message(self) -> str | None:
        return NO_BACKING if self.backing_passage is None else None
