"""M12 · Clase del docente.

Stub: returns example data so the front can integrate. The real use cases replace each body.
Teacher-only routes document the 403 but the stub does not check the role yet.
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from frobi.modules.classrooms.domain.errors import InvalidClassCode
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    TEACHER_RESPONSES,
    problem,
    require_token,
)

from .schemas import (
    AiUsage,
    Alert,
    ClassMaterialOut,
    ClassOut,
    CreateClassRequest,
    DashboardOut,
    FailedQuestion,
    FormatCount,
    HelpByStep,
    InvitationsRequest,
    JoinClassOut,
    JoinClassRequest,
    MemberOut,
    MembershipStatus,
    MembersOut,
    StudentDetailOut,
    StudentRow,
)

router = APIRouter(
    prefix="/classes",
    tags=["M12 · Clase del docente"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

EXAMPLE_CLASS_ID = UUID("00000000-0000-4000-8000-0000000000c1")
EXAMPLE_CODE = "SENSOR1"
STUDENT_1 = UUID("00000000-0000-4000-8000-000000000001")
STUDENT_2 = UUID("00000000-0000-4000-8000-000000000002")
CREATED_AT = datetime(2026, 11, 4, 9, 0, tzinfo=UTC)
_LABELS = {
    MembershipStatus.INVITED: "Invitación pendiente",
    MembershipStatus.JOINED: "Se unió",
    MembershipStatus.LEFT: "Salió de la clase",
}
TEACHER_ONLY = {**TEACHER_RESPONSES, **NOT_FOUND_RESPONSES}


def _class(class_id: UUID, name: str, subject: str, tasks: list[str]) -> ClassOut:
    return ClassOut(
        id=class_id,
        name=name,
        subject=subject,
        tasks=tasks,
        invite_code=EXAMPLE_CODE,
        created_at=CREATED_AT,
    )


def _member(alias: str, person_id: UUID | None, member_status: MembershipStatus) -> MemberOut:
    return MemberOut(
        alias=alias,
        person_id=person_id,
        status=member_status,
        status_label=_LABELS[member_status],
        joined_at=CREATED_AT if member_status is MembershipStatus.JOINED else None,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crear una clase y su código de invitación",
    responses=TEACHER_RESPONSES,
)
async def create_class(body: CreateClassRequest) -> ClassOut:
    return _class(EXAMPLE_CLASS_ID, body.name, body.subject, body.tasks)


@router.post(
    "/join",
    summary="Unirse a una clase con su código (estudiante)",
    responses={422: problem("Código inexistente (`Classrooms.InvalidCode`).")},
)
async def join_class(body: JoinClassRequest) -> JoinClassOut:
    if body.code.strip().upper() != EXAMPLE_CODE:
        raise InvalidClassCode()
    return JoinClassOut(class_id=EXAMPLE_CLASS_ID, class_name="Sensores 2026-II")


@router.get("/{class_id}", summary="Detalle de la clase", responses=NOT_FOUND_RESPONSES)
async def get_class(class_id: UUID) -> ClassOut:
    return _class(
        class_id, "Sensores 2026-II", "Instrumentación", ["Leer la guía", "Entregar el informe"]
    )


@router.post(
    "/{class_id}/materials",
    status_code=status.HTTP_201_CREATED,
    summary="Subir contenido de la clase (texto o PDF)",
    responses={**TEACHER_ONLY, 422: problem("Falta `text` o `file`, o el PDF es ilegible.")},
)
async def upload_class_material(
    class_id: UUID,
    title: Annotated[str, Form(min_length=1, max_length=120)],
    text: Annotated[str | None, Form(max_length=100_000)] = None,
    file: Annotated[UploadFile | None, File(description="PDF de hasta 10 MB.")] = None,
) -> ClassMaterialOut:
    return ClassMaterialOut(
        id=UUID("00000000-0000-4000-8000-00000000a010"),
        class_id=class_id,
        title=title,
        extracted_text=text or "Texto extraído del PDF de la clase.",
    )


@router.post(
    "/{class_id}/invitations",
    status_code=status.HTTP_201_CREATED,
    summary="Invitar estudiantes por alias",
    responses=TEACHER_ONLY,
)
async def invite_students(class_id: UUID, body: InvitationsRequest) -> list[MemberOut]:
    return [_member(alias, None, MembershipStatus.INVITED) for alias in body.aliases]


@router.get(
    "/{class_id}/members",
    summary="Código y lista de miembros con su estado",
    responses=TEACHER_ONLY,
)
async def list_members(class_id: UUID) -> MembersOut:
    return MembersOut(
        invite_code=EXAMPLE_CODE,
        members=[
            _member("Ana", STUDENT_1, MembershipStatus.JOINED),
            _member("Luis", STUDENT_2, MembershipStatus.JOINED),
            _member("Rosa", None, MembershipStatus.INVITED),
        ],
    )


@router.get("/{class_id}/dashboard", summary="Panel docente", responses=TEACHER_ONLY)
async def get_dashboard(class_id: UUID) -> DashboardOut:
    return DashboardOut(
        class_id=class_id,
        sample_data=True,
        students=[
            StudentRow(person_id=STUDENT_1, alias="Ana", progress_label="Va bien", alerts=[]),
            StudentRow(
                person_id=STUDENT_2,
                alias="Luis",
                progress_label="Necesita apoyo",
                alerts=[Alert(code="stuck_on_hint_1", text="Se traba en la pista 1", icon="help")],
            ),
        ],
        top_formats=[
            FormatCount(format="easy_read", count=7),
            FormatCount(format="visual_map", count=4),
        ],
        most_failed_questions=[
            FailedQuestion(statement="¿Qué sensor detecta una botella de plástico?", fail_rate=0.4)
        ],
        ai_usage=AiUsage(help_requests=12, solved_without_ai=5),
    )


@router.get(
    "/{class_id}/students/{person_id}",
    summary="Detalle de un estudiante (solo actividad de esta clase)",
    responses=TEACHER_ONLY,
)
async def get_student(class_id: UUID, person_id: UUID) -> StudentDetailOut:
    return StudentDetailOut(
        person_id=person_id,
        alias="Luis",
        preferred_format="visual_map",
        correct_answers=3,
        total_answers=6,
        help_by_step=[
            HelpByStep(step="hint_1", count=4),
            HelpByStep(step="hint_2", count=2),
        ],
        solved_without_ai=1,
        most_failed_question="¿Qué sensor detecta una botella de plástico?",
    )
