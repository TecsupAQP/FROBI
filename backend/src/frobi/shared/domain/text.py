"""Plain-text matching without AI: accent-insensitive keywords and sentence splitting."""

import re
import unicodedata
from collections.abc import Iterable

_WORD = re.compile(r"[a-z0-9]+")
_SENTENCE = re.compile(r"(?<=[.!?])\s+")

# Frequent Spanish words of 5+ letters that say nothing about the topic.
STOPWORDS = frozenset(
    {
        "como", "cual", "cuales", "cuando", "debe", "deben", "donde", "entre", "esta", "este",
        "estos", "estas", "para", "pero", "porque", "puede", "pueden", "sobre", "tiene",
        "tienen", "todo", "todos", "tambien", "hacer", "cada", "desde", "hasta", "segun",
        "siempre", "nunca", "mucho", "muchos", "otros", "otras", "mismo", "misma", "algun",
        "alguna", "algunos", "entonces", "aunque", "mientras", "despues", "antes",
    }
)  # fmt: skip


def fold(text: str) -> str:
    """Lowercase without accents: «Conclusión» → «conclusion»."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def singular(word: str) -> str:
    """Light Spanish plural folding: sensores → sensor, plásticos → plastico, metales → metal."""
    if len(word) > 5 and word.endswith("es") and word[-3] in "rlndzj":
        return word[:-2]
    if len(word) > 4 and word.endswith("s"):
        return word[:-1]
    return word


def keywords(text: str, *, min_length: int = 5, extra_stopwords: Iterable[str] = ()) -> set[str]:
    """Topic words of ``text``: folded, singular, at least ``min_length`` letters."""
    stop = STOPWORDS | set(extra_stopwords)
    return {
        singular(w) for w in _WORD.findall(fold(text)) if len(w) >= min_length and w not in stop
    }


STEM_LENGTH = 6


def stem(word: str) -> str:
    """Crude root for matching word families: afectados / afectarlos → afecta, preciso / precisa →
    precis. Only for comparing texts, never shown to anyone."""
    return singular(fold(word))[:STEM_LENGTH]


def stems(text: str, *, min_length: int = 5) -> set[str]:
    """Roots of the topic words of ``text`` (see ``keywords`` and ``stem``)."""
    return {w[:STEM_LENGTH] for w in keywords(text, min_length=min_length)}


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE.split(text) if s.strip()]
