"""M1 · Cuenta y acceso: contract with the front."""

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Role(StrEnum):
    LEARNER = "learner"
    TEACHER = "teacher"


class ConfiguredBy(StrEnum):
    SELF = "self"
    COMPANION = "companion"


class IntroStatus(StrEnum):
    SEEN = "seen"
    SKIPPED = "skipped"
    PENDING = "pending"


class CreateSessionRequest(BaseModel):
    alias: str = Field(min_length=1, max_length=40, examples=["Ana"])
    career: str = Field(min_length=1, max_length=80, examples=["Mecatrónica"])
    role: Role
    class_code: str | None = Field(
        default=None,
        max_length=16,
        description="Opcional. Si no existe se responde 422 `Classrooms.InvalidCode`.",
        examples=["SENSOR1"],
    )


class PersonOut(BaseModel):
    id: UUID
    alias: str
    career: str
    role: Role
    configured_by: ConfiguredBy


class ActiveMembershipOut(BaseModel):
    class_id: UUID
    class_name: str
    status: Literal["joined"] = "joined"


class SessionOut(BaseModel):
    token: str = Field(description="Enviar como `Authorization: Bearer <token>`. Dura 30 días.")
    person: PersonOut
    membership: ActiveMembershipOut | None


class OnboardingStateOut(BaseModel):
    done: bool
    intro_status: IntroStatus


class MeOut(BaseModel):
    person: PersonOut
    membership: ActiveMembershipOut | None
    onboarding: OnboardingStateOut
