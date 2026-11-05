"""«Completa la frase» questions built only from the person's own text (no AI).

A sentence of the material loses one topic word; the options are that word and two other topic
words of the same material. Option order is alphabetical, so the right one is not always «a».
"""

import re

from frobi.shared.domain import text

from .question import Option, QuestionDraft

LETTERS = "abcde"
_TOKEN = re.compile(r"\w+", re.UNICODE)


def _content_sentences(material_text: str) -> list[str]:
    lines = [line for line in material_text.splitlines() if line and not line.startswith("#")]
    return [s for s in text.sentences(" ".join(lines)) if 6 <= len(s.split()) <= 40]


def _topic_words(sentence: str) -> list[str]:
    """Words of the sentence (as written) that are topic keywords, longest first."""
    keys = text.keywords(sentence, min_length=6)
    words = [w for w in _TOKEN.findall(sentence) if text.singular(text.fold(w)) in keys]
    return sorted(dict.fromkeys(words), key=len, reverse=True)


def cloze_questions(material_text: str, n: int, *, skip: int = 0) -> list[QuestionDraft]:
    sentences = _content_sentences(material_text)
    pool = sorted({w for s in sentences for w in _topic_words(s)}, key=lambda w: text.fold(w))
    drafts: list[QuestionDraft] = []
    used: set[str] = set()
    for sentence in sentences[skip:]:
        if len(drafts) == n:
            break
        candidates = [w for w in _topic_words(sentence) if text.fold(w) not in used]
        if not candidates:
            continue
        answer = candidates[0]
        others = [
            w
            for w in sorted(pool, key=lambda w: (abs(len(w) - len(answer)), text.fold(w)))
            if text.fold(w) != text.fold(answer) and text.fold(w) not in text.fold(sentence)
        ][:2]
        if len(others) < 2:
            continue
        words = sorted([answer, *others], key=lambda w: text.fold(w))
        options = tuple(Option(LETTERS[i], w) for i, w in enumerate(words))
        blanked = re.sub(rf"\b{re.escape(answer)}\b", "_____", sentence, count=1)
        drafts.append(
            QuestionDraft(
                statement=f"Completa según tu material: «{blanked}»",
                options=options,
                correct_option=LETTERS[words.index(answer)],
                feedback_correct=f"Bien. Tu material dice: «{sentence}»",
                feedback_wrong=f"Revisa esta frase de tu material: «{sentence}»",
            ).validate()
        )
        used.add(text.fold(answer))
    return drafts
