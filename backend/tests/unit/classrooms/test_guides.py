"""Guías de la clase: de estudio (evaluación final) o con tareas, y su porcentaje de avance."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from frobi.modules.classrooms.application.guides import guide_progress
from frobi.modules.classrooms.domain import (
    GuideMode,
    GuidePlan,
    InvalidGuidePlan,
    task_ref_of,
)
from frobi.shared.application import GuideAdaptation, QuestionResult, TaskAttempt

ANA = uuid4()
LUIS = uuid4()
CLASE = uuid4()
GUIA = uuid4()
T0 = datetime(2026, 11, 5, 10, tzinfo=UTC)


def _plan_tareas(*enunciados: str) -> GuidePlan:
    return GuidePlan.create(GUIA, CLASE, GuideMode.TASKS, list(enunciados))


def _adaptacion(persona: UUID, minutos: int, material: UUID = GUIA) -> GuideAdaptation:
    return GuideAdaptation(uuid4(), persona, material, T0 + timedelta(minutes=minutos))


def _pregunta(
    persona: UUID, adaptacion: GuideAdaptation, respondida: bool, correcta: bool
) -> QuestionResult:
    return QuestionResult(persona, adaptacion.adaptation_id, uuid4(), respondida, correcta)


# --- Reglas del plan ------------------------------------------------------------------------


def test_a_study_guide_has_no_tasks() -> None:
    plan = GuidePlan.create(GUIA, CLASE, GuideMode.STUDY, [])

    assert plan.mode is GuideMode.STUDY
    assert plan.tasks == ()


def test_a_study_guide_rejects_tasks() -> None:
    with pytest.raises(InvalidGuidePlan):
        GuidePlan.create(GUIA, CLASE, GuideMode.STUDY, ["Resuelve el ejercicio 1"])


def test_a_task_guide_needs_at_least_one_task() -> None:
    with pytest.raises(InvalidGuidePlan):
        GuidePlan.create(GUIA, CLASE, GuideMode.TASKS, ["  ", ""])


def test_tasks_are_cleaned_and_kept_in_order() -> None:
    plan = _plan_tareas("  Explica   el motor ", "Compara dos motores", "Explica el motor")

    assert [t.statement for t in plan.tasks] == ["Explica el motor", "Compara dos motores"]
    assert [t.position for t in plan.tasks] == [1, 2]


def test_a_task_guide_has_at_most_twenty_tasks() -> None:
    with pytest.raises(InvalidGuidePlan):
        _plan_tareas(*[f"Tarea {n}" for n in range(21)])


def test_each_task_has_its_own_help_ladder_reference() -> None:
    tarea = _plan_tareas("Explica el motor").tasks[0]

    assert task_ref_of(tarea.id) == f"tarea-{tarea.id}"


# --- Avance de una guía con tareas -----------------------------------------------------------


def test_task_progress_counts_tasks_with_an_own_answer() -> None:
    plan = _plan_tareas("Tarea 1", "Tarea 2", "Tarea 3", "Tarea 4")
    t1, t2, t3, _ = plan.tasks
    intentos = [
        TaskAttempt(ANA, task_ref_of(t1.id), own_answer=True),
        TaskAttempt(ANA, task_ref_of(t2.id), own_answer=False),  # solo pidió pistas
        TaskAttempt(ANA, task_ref_of(t3.id), own_answer=True),
        TaskAttempt(LUIS, task_ref_of(t1.id), own_answer=True),  # de otra persona
    ]

    avance = guide_progress(plan, ANA, adaptations=[], questions=[], attempts=intentos)

    assert avance.completion == 50
    assert avance.done_task_ids == (t1.id, t3.id)
    assert avance.evaluation is None


def test_a_task_counts_once_even_with_several_attempts() -> None:
    plan = _plan_tareas("Tarea 1", "Tarea 2")
    t1 = plan.tasks[0]
    intentos = [TaskAttempt(ANA, task_ref_of(t1.id), own_answer=True)] * 3

    assert guide_progress(plan, ANA, [], [], intentos).completion == 50


# --- Avance de una guía de estudio (evaluación final) ----------------------------------------


def test_study_progress_is_zero_before_the_final_evaluation() -> None:
    plan = GuidePlan.create(GUIA, CLASE, GuideMode.STUDY, [])

    avance = guide_progress(plan, ANA, [_adaptacion(ANA, 0)], [], [])

    assert avance.completion == 0
    assert avance.evaluation is None


def test_study_progress_is_the_score_of_the_latest_evaluation() -> None:
    plan = GuidePlan.create(GUIA, CLASE, GuideMode.STUDY, [])
    primera = _adaptacion(ANA, 0)
    ultima = _adaptacion(ANA, 30)
    preguntas = [
        # Primera evaluación: 0 de 2
        _pregunta(ANA, primera, respondida=True, correcta=False),
        _pregunta(ANA, primera, respondida=True, correcta=False),
        # Última evaluación: 2 de 3 (una sin responder cuenta como no acertada)
        _pregunta(ANA, ultima, respondida=True, correcta=True),
        _pregunta(ANA, ultima, respondida=True, correcta=True),
        _pregunta(ANA, ultima, respondida=False, correcta=False),
    ]

    avance = guide_progress(plan, ANA, [primera, ultima], preguntas, [])

    assert avance.evaluation == (2, 3)
    assert avance.completion == 67


def test_an_evaluation_without_answers_does_not_count() -> None:
    plan = GuidePlan.create(GUIA, CLASE, GuideMode.STUDY, [])
    respondida = _adaptacion(ANA, 0)
    sin_responder = _adaptacion(ANA, 30)
    preguntas = [
        _pregunta(ANA, respondida, respondida=True, correcta=True),
        _pregunta(ANA, sin_responder, respondida=False, correcta=False),
    ]

    avance = guide_progress(plan, ANA, [respondida, sin_responder], preguntas, [])

    assert avance.evaluation == (1, 1)
    assert avance.completion == 100


def test_study_progress_only_uses_this_guide_and_this_person() -> None:
    plan = GuidePlan.create(GUIA, CLASE, GuideMode.STUDY, [])
    otra_guia = _adaptacion(ANA, 10, material=uuid4())
    de_luis = _adaptacion(LUIS, 20)
    preguntas = [
        _pregunta(ANA, otra_guia, respondida=True, correcta=True),
        _pregunta(LUIS, de_luis, respondida=True, correcta=True),
    ]

    avance = guide_progress(plan, ANA, [otra_guia, de_luis], preguntas, [])

    assert avance.completion == 0
