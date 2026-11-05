from datetime import UTC, datetime
from uuid import uuid4

from frobi.modules.progress.application import EMPTY_MESSAGE, journey_of, progress_of
from frobi.modules.progress.application.ports import PersonActivity, RecipeView
from frobi.shared.application import AnswerRow, FormatUse, HelpUse, PromptScoreRow

ANA = uuid4()
T = datetime(2026, 11, 6, 10, 0, tzinfo=UTC)


def _answer(fmt: str, ok: bool) -> AnswerRow:
    return AnswerRow(ANA, uuid4(), "¿Pregunta?", fmt, ok, True, T)


def _activity(**kwargs: object) -> PersonActivity:
    base: dict[str, object] = {
        "formats": [],
        "help": [],
        "answers": [],
        "prompt_scores": [],
        "latest_recipe": None,
    }
    base.update(kwargs)
    return PersonActivity(**base)  # type: ignore[arg-type]


def test_no_activity_is_an_explicit_empty_state() -> None:
    progress = progress_of(_activity())

    assert progress.has_data is False
    assert progress.message == EMPTY_MESSAGE


def test_the_message_names_the_best_format_the_score_trend_and_solved_without_ai() -> None:
    activity = _activity(
        formats=[FormatUse(ANA, "easy_read", T), FormatUse(ANA, "audio", T)],
        answers=[
            _answer("easy_read", True),
            _answer("easy_read", True),
            _answer("audio", False),
            _answer("audio", False),
        ],
        prompt_scores=[PromptScoreRow(ANA, 4, 1, T), PromptScoreRow(ANA, 13, 3, T)],
        help=[HelpUse(ANA, "none", True, True)],
    )

    message = progress_of(activity).message

    assert message == (
        "Aciertas más con lectura fácil, tus instrucciones mejoraron de 4 a 13 de 16 y "
        "resolviste 1 tarea sin IA."
    )


def test_with_few_answers_it_counts_them_instead() -> None:
    activity = _activity(answers=[_answer("audio", False), _answer("easy_read", True)])

    assert progress_of(activity).message == "Llevas 1 de 2 aciertos."


def test_journey_summary() -> None:
    recipe = RecipeView("Estudio la guía", "Entender", "Simple", "easy_read")
    activity = _activity(
        formats=[FormatUse(ANA, "audio", T), FormatUse(ANA, "audio", T)],
        prompt_scores=[PromptScoreRow(ANA, 15, 3, T), PromptScoreRow(ANA, 9, 2, T)],
        latest_recipe=recipe,
    )

    journey = journey_of(activity)

    assert journey.favorite_format == "audio"
    assert journey.learned_recipe == recipe
    assert journey.best_prompt_score == 15
    assert journey.autonomy_level == 2
    assert journey.message.startswith("Ya pides con contexto")
