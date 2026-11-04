"""M12 · Clase del docente: contract with the front."""

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MembershipStatus(StrEnum):
    INVITED = "invited"
    JOINED = "joined"
    LEFT = "left"


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


class ClassMaterialOut(BaseModel):
    id: UUID
    class_id: UUID
    title: str
    kind: Literal["class_content"] = "class_content"
    extracted_text: str


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
