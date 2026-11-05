"""M1 · Cuenta y acceso: contract with the front."""

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.identity.application import MeView, StartSessionResult
from frobi.modules.identity.application.ports import ActiveMembership
from frobi.modules.identity.domain import ConfiguredBy, Person, Role


class IntroStatus(StrEnum):
    SEEN = "seen"
    SKIPPED = "skipped"
    PENDING = "pending"


class DemoSessionRequest(BaseModel):
    who: Literal["teacher", "ana", "luis"] = Field(
        description="`teacher`: docente demo de SENSOR1. `ana` y `luis`: sus estudiantes demo."
    )


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

    @classmethod
    def from_domain(cls, person: Person) -> "PersonOut":
        return cls(
            id=person.id,
            alias=person.alias,
            career=person.career,
            role=person.role,
            configured_by=person.configured_by,
        )


class ActiveMembershipOut(BaseModel):
    class_id: UUID
    class_name: str
    status: Literal["joined"] = "joined"

    @classmethod
    def from_port(cls, membership: ActiveMembership | None) -> "ActiveMembershipOut | None":
        if membership is None:
            return None
        return cls(class_id=membership.class_id, class_name=membership.class_name)


class SessionOut(BaseModel):
    token: str = Field(description="Enviar como `Authorization: Bearer <token>`. Dura 30 días.")
    person: PersonOut
    membership: ActiveMembershipOut | None

    @classmethod
    def from_result(cls, result: StartSessionResult) -> "SessionOut":
        return cls(
            token=result.token,
            person=PersonOut.from_domain(result.person),
            membership=ActiveMembershipOut.from_port(result.membership),
        )


class OnboardingStateOut(BaseModel):
    done: bool
    intro_status: IntroStatus


class MeOut(BaseModel):
    person: PersonOut
    membership: ActiveMembershipOut | None
    onboarding: OnboardingStateOut

    @classmethod
    def from_view(cls, view: MeView) -> "MeOut":
        return cls(
            person=PersonOut.from_domain(view.person),
            membership=ActiveMembershipOut.from_port(view.membership),
            onboarding=OnboardingStateOut(
                done=view.onboarding.done, intro_status=IntroStatus(view.onboarding.intro_status)
            ),
        )
