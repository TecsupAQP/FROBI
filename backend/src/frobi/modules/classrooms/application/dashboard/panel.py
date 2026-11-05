"""What the teacher panel shows, computed from the class activity (RF17, RF25, RF47, RNF17).

Alerts are written as help, never as blame («Se traba en la pista 1», not «no entiende»).
Thresholds are named constants: the requirements call them «propuesta por validar».
"""

from collections import Counter
from dataclasses import dataclass
from uuid import UUID

from frobi.modules.classrooms.application.ports import ClassActivity
from frobi.shared.application import AnswerRow

STUCK_ATTEMPTS = 2  # attempts that stop at hint 1 without an own answer
LOW_ACCURACY = 0.5  # share of right answers below which a student «needs to review»
MIN_ANSWERS_FOR_ACCURACY = 3
MIN_ANSWERS_PER_QUESTION = 2
TOP = 3

ALERTS = {
    "stuck_on_hint_1": ("Se traba en la pista 1", "help"),
    "needs_review": ("Le conviene repasar: acierta menos de la mitad", "book"),
    "not_started": ("Todavía no empezó", "clock"),
}


@dataclass(frozen=True, slots=True)
class Alert:
    code: str
    text: str
    icon: str


def alert(code: str) -> Alert:
    text, icon = ALERTS[code]
    return Alert(code, text, icon)


@dataclass(frozen=True, slots=True)
class StudentSummary:
    person_id: UUID
    alias: str
    progress_label: str
    alerts: tuple[Alert, ...]


@dataclass(frozen=True, slots=True)
class FailedQuestion:
    statement: str
    fail_rate: float


@dataclass(frozen=True, slots=True)
class Panel:
    class_id: UUID
    sample_data: bool
    students: tuple[StudentSummary, ...]
    top_formats: tuple[tuple[str, int], ...]
    most_failed_questions: tuple[FailedQuestion, ...]
    help_requests: int
    solved_without_ai: int


def _student(person_id: UUID, alias: str, activity: ClassActivity) -> StudentSummary:
    formats = [f for f in activity.formats if f.person_id == person_id]
    attempts = [h for h in activity.help if h.person_id == person_id]
    answers = [a for a in activity.answers if a.person_id == person_id]
    scores = [s for s in activity.prompt_scores if s.person_id == person_id]
    alerts: list[Alert] = []
    if not (formats or attempts or answers or scores):
        alerts.append(alert("not_started"))
    stuck = [h for h in attempts if h.max_step == "hint_1" and not h.own_answer]
    if len(stuck) >= STUCK_ATTEMPTS:
        alerts.append(alert("stuck_on_hint_1"))
    if len(answers) >= MIN_ANSWERS_FOR_ACCURACY:
        accuracy = sum(a.is_correct for a in answers) / len(answers)
        if accuracy < LOW_ACCURACY:
            alerts.append(alert("needs_review"))
    if any(a.code == "not_started" for a in alerts):
        label = "Sin actividad todavía"
    elif alerts:
        label = "Necesita apoyo"
    else:
        label = "Va bien"
    return StudentSummary(person_id, alias, label, tuple(alerts))


def most_failed(answers: list[AnswerRow]) -> tuple[FailedQuestion, ...]:
    by_statement: dict[str, list[bool]] = {}
    for answer in answers:
        by_statement.setdefault(answer.statement, []).append(answer.is_correct)
    failed = [
        FailedQuestion(statement, round(results.count(False) / len(results), 2))
        for statement, results in by_statement.items()
        if len(results) >= MIN_ANSWERS_PER_QUESTION and not all(results)
    ]
    return tuple(sorted(failed, key=lambda q: (-q.fail_rate, q.statement))[:TOP])


def build_panel(class_id: UUID, students: list[tuple[UUID, str]], activity: ClassActivity) -> Panel:
    return Panel(
        class_id=class_id,
        sample_data=False,
        students=tuple(_student(pid, alias, activity) for pid, alias in students),
        top_formats=tuple(Counter(f.format for f in activity.formats).most_common(TOP)),
        most_failed_questions=most_failed(activity.answers),
        help_requests=sum(
            ["none", "hint_1", "hint_2", "step_by_step", "final"].index(h.max_step)
            for h in activity.help
        ),
        solved_without_ai=sum(h.solved_without_ai for h in activity.help),
    )


SAMPLE_STUDENT_1 = UUID("00000000-0000-4000-8000-000000000001")
SAMPLE_STUDENT_2 = UUID("00000000-0000-4000-8000-000000000002")


def sample_panel(class_id: UUID) -> Panel:
    """Shown while the class has no real activity, flagged ``sample_data`` (RNF12)."""
    return Panel(
        class_id=class_id,
        sample_data=True,
        students=(
            StudentSummary(SAMPLE_STUDENT_1, "Ana (ejemplo)", "Va bien", ()),
            StudentSummary(
                SAMPLE_STUDENT_2,
                "Luis (ejemplo)",
                "Necesita apoyo",
                (alert("stuck_on_hint_1"),),
            ),
        ),
        top_formats=(("easy_read", 7), ("visual_map", 4)),
        most_failed_questions=(
            FailedQuestion("¿Qué sensor detecta una botella de plástico?", 0.4),
        ),
        help_requests=12,
        solved_without_ai=5,
    )


@dataclass(frozen=True, slots=True)
class StudentDetail:
    person_id: UUID
    alias: str
    preferred_format: str | None
    correct_answers: int
    total_answers: int
    help_by_step: tuple[tuple[str, int], ...]
    solved_without_ai: int
    most_failed_question: str | None


def build_student_detail(person_id: UUID, alias: str, activity: ClassActivity) -> StudentDetail:
    formats = Counter(f.format for f in activity.formats if f.person_id == person_id)
    answers = [a for a in activity.answers if a.person_id == person_id]
    attempts = [h for h in activity.help if h.person_id == person_id]
    steps = Counter(h.max_step for h in attempts if h.max_step != "none")
    failed = most_failed(answers) or tuple(
        FailedQuestion(a.statement, 1.0) for a in answers if not a.is_correct
    )
    return StudentDetail(
        person_id=person_id,
        alias=alias,
        preferred_format=formats.most_common(1)[0][0] if formats else None,
        correct_answers=sum(a.is_correct for a in answers),
        total_answers=len(answers),
        help_by_step=tuple(
            (step, steps[step])
            for step in ("hint_1", "hint_2", "step_by_step", "final")
            if steps[step]
        ),
        solved_without_ai=sum(h.solved_without_ai for h in attempts),
        most_failed_question=failed[0].statement if failed else None,
    )
