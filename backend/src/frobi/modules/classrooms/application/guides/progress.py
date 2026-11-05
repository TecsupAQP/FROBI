"""Porcentaje de avance de una guía, a partir de la actividad hecha dentro de la clase."""

from datetime import datetime
from uuid import UUID

from frobi.modules.classrooms.domain import GuideMode, GuidePlan, GuideProgress, task_ref_of
from frobi.shared.application import GuideAdaptation, QuestionResult, TaskAttempt


def _latest_evaluation(
    plan: GuidePlan,
    person_id: UUID,
    adaptations: list[GuideAdaptation],
    questions: list[QuestionResult],
) -> tuple[int, int] | None:
    own: dict[UUID, datetime] = {
        a.adaptation_id: a.created_at
        for a in adaptations
        if a.person_id == person_id and a.material_id == plan.material_id
    }
    by_adaptation: dict[UUID, list[QuestionResult]] = {}
    for question in questions:
        if question.person_id == person_id and question.adaptation_id in own:
            by_adaptation.setdefault(question.adaptation_id, []).append(question)
    answered = [
        (own[adaptation_id], results)
        for adaptation_id, results in by_adaptation.items()
        if any(r.answered for r in results)
    ]
    if not answered:
        return None
    _, results = max(answered, key=lambda item: item[0])
    return sum(1 for r in results if r.correct), len(results)


def guide_progress(
    plan: GuidePlan,
    person_id: UUID,
    adaptations: list[GuideAdaptation],
    questions: list[QuestionResult],
    attempts: list[TaskAttempt],
) -> GuideProgress:
    if plan.mode is GuideMode.TASKS:
        done_refs = {a.task_ref for a in attempts if a.person_id == person_id and a.own_answer}
        done = tuple(task.id for task in plan.tasks if task_ref_of(task.id) in done_refs)
        percent = round(100 * len(done) / len(plan.tasks)) if plan.tasks else 0
        return GuideProgress(plan.material_id, plan.mode, percent, done, None)
    evaluation = _latest_evaluation(plan, person_id, adaptations, questions)
    percent = round(100 * evaluation[0] / evaluation[1]) if evaluation and evaluation[1] else 0
    return GuideProgress(plan.material_id, plan.mode, percent, (), evaluation)
