"""M12 · Clase del docente: contract with the front."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.classrooms.domain import MAX_TASKS, GuideMode, MembershipStatus


class CreateClassRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    subject: str = Field(min_length=1, max_length=80)
    tasks: list[str] = Field(default_factory=list, max_length=20)


class ClassOut(BaseModel):
    id: UUID
    name: str
    subject: str
    tasks: list[str]
    invite_code: str
    created_at: datetime


class GuideTaskOut(BaseModel):
    id: UUID
    position: int
    statement: str
    task_ref: str = Field(
        description="Lo que se envía como `task_ref` al abrir la escalera de ayuda de esta tarea."
    )


class ClassMaterialOut(BaseModel):
    id: UUID
    class_id: UUID
    title: str
    kind: Literal["class_content"] = "class_content"
    extracted_text: str
    mode: GuideMode = Field(
        default=GuideMode.STUDY,
        description="`study`: la IA evalúa al final. `tasks`: tiene tareas del docente.",
    )
    tasks: list[GuideTaskOut] = Field(default_factory=list)


class ClassMaterialSummaryOut(BaseModel):
    id: UUID
    class_id: UUID
    title: str
    kind: Literal["class_content"] = "class_content"
    preview: str = Field(description="Primeras líneas del texto.")
    created_at: datetime
    mode: GuideMode = GuideMode.STUDY
    tasks: list[GuideTaskOut] = Field(default_factory=list)


class GuidePlanRequest(BaseModel):
    mode: GuideMode
    tasks: list[str] = Field(default_factory=list, max_length=MAX_TASKS)


class GuidePlanOut(BaseModel):
    material_id: UUID
    mode: GuideMode
    tasks: list[GuideTaskOut]


class EvaluationOut(BaseModel):
    correct: int
    total: int


class GuideProgressOut(BaseModel):
    material_id: UUID
    mode: GuideMode
    completion: int = Field(ge=0, le=100, description="Avance de la guía, de 0 a 100.")
    done_task_ids: list[UUID] = Field(description="Tareas con intento propio (guía con tareas).")
    evaluation: EvaluationOut | None = Field(
        description="Última evaluación final respondida (guía de estudio); null si aún no hay."
    )


class StudentGuideProgressOut(BaseModel):
    person_id: UUID
    alias: str
    completion: int = Field(ge=0, le=100, description="Avance de la guía, de 0 a 100.")


class GuideClassProgressOut(BaseModel):
    material_id: UUID
    title: str
    mode: GuideMode
    tasks_total: int
    students: list[StudentGuideProgressOut]


class InvitationsRequest(BaseModel):
    aliases: list[str] = Field(min_length=1, max_length=60)


class MemberOut(BaseModel):
    alias: str
    person_id: UUID | None = Field(description="`null` mientras la invitación está pendiente.")
    status: MembershipStatus
    status_label: str = Field(examples=["Se unió", "Invitación pendiente"])
    joined_at: datetime | None


class MembersOut(BaseModel):
    invite_code: str
    members: list[MemberOut]


class JoinClassRequest(BaseModel):
    code: str = Field(min_length=1, max_length=16)


class JoinClassOut(BaseModel):
    class_id: UUID
    class_name: str
    status: Literal["joined"] = "joined"


class Alert(BaseModel):
    code: str = Field(examples=["stuck_on_hint_1"])
    text: str = Field(examples=["Se traba en la pista 1"])
    icon: str


class StudentRow(BaseModel):
    person_id: UUID
    alias: str
    progress_label: str
    alerts: list[Alert]


class FormatCount(BaseModel):
    format: Literal["visual_map", "real_example", "easy_read", "audio"]
    count: int = Field(ge=0)


class FailedQuestion(BaseModel):
    statement: str
    fail_rate: float = Field(ge=0, le=1)


class AiUsage(BaseModel):
    help_requests: int = Field(ge=0)
    solved_without_ai: int = Field(ge=0)


class DashboardOut(BaseModel):
    class_id: UUID
    sample_data: bool = Field(description="`true` mientras se muestran datos de ejemplo.")
    students: list[StudentRow]
    top_formats: list[FormatCount]
    most_failed_questions: list[FailedQuestion]
    ai_usage: AiUsage


class HelpByStep(BaseModel):
    step: Literal["hint_1", "hint_2", "step_by_step", "final"]
    count: int = Field(ge=0)


class StudentDetailOut(BaseModel):
    """Only activity recorded with this class_id (RNF16)."""

    person_id: UUID
    alias: str
    preferred_format: Literal["visual_map", "real_example", "easy_read", "audio"] | None
    correct_answers: int = Field(ge=0)
    total_answers: int = Field(ge=0)
    help_by_step: list[HelpByStep]
    solved_without_ai: int = Field(ge=0)
    most_failed_question: str | None
