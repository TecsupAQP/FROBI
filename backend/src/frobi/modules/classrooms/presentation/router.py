"""M12 · Clase del docente.

Real: create a class, join with a code, see the class, invite by alias, list members.
Still stubs (example data): class materials and the student detail (phase 3).
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from frobi.modules.classrooms.application import (
    CreateClassCommand,
    CreateClassHandler,
    GetClassHandler,
    InviteStudentsHandler,
    JoinWithCodeHandler,
    ListMembersHandler,
)
from frobi.modules.classrooms.domain import Classroom, Membership
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    TEACHER_RESPONSES,
    CurrentPersonId,
    problem,
)

from .dependencies import (
    get_create_class,
    get_get_class,
    get_invite_students,
    get_join_class,
    get_list_members,
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
    MembersOut,
    StudentDetailOut,
    StudentRow,
)

router = APIRouter(prefix="/classes", tags=["M12 · Clase del docente"], responses=AUTH_RESPONSES)

TEACHER_ONLY = {**TEACHER_RESPONSES, **NOT_FOUND_RESPONSES}
STUDENT_1 = UUID("00000000-0000-4000-8000-000000000001")
STUDENT_2 = UUID("00000000-0000-4000-8000-000000000002")


def _class_out(classroom: Classroom) -> ClassOut:
    return ClassOut(
        id=classroom.id,
        name=classroom.name,
        subject=classroom.subject,
        tasks=list(classroom.tasks),
        invite_code=classroom.invite_code,
        created_at=classroom.created_at,
    )


def _member_out(membership: Membership) -> MemberOut:
    return MemberOut(
        alias=membership.alias,
        person_id=membership.person_id,
        status=membership.status,
        status_label=membership.status_label,
        joined_at=membership.joined_at,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crear una clase y su código de invitación",
    responses={**TEACHER_RESPONSES, 422: problem("Datos de la clase inválidos.")},
)
async def create_class(
    body: CreateClassRequest,
    person_id: CurrentPersonId,
    handler: Annotated[CreateClassHandler, Depends(get_create_class)],
) -> ClassOut:
    classroom = await handler.handle(
        CreateClassCommand(
            teacher_id=person_id, name=body.name, subject=body.subject, tasks=body.tasks
        )
    )
    return _class_out(classroom)


@router.post(
    "/join",
    summary="Unirse a una clase con su código (estudiante)",
    responses={422: problem("Código inexistente (`Classrooms.InvalidCode`).")},
)
async def join_class(
    body: JoinClassRequest,
    person_id: CurrentPersonId,
    handler: Annotated[JoinWithCodeHandler, Depends(get_join_class)],
) -> JoinClassOut:
    joined = await handler.handle(person_id, body.code)
    return JoinClassOut(class_id=joined.class_id, class_name=joined.class_name)


@router.get("/{class_id}", summary="Detalle de la clase", responses=NOT_FOUND_RESPONSES)
async def get_class(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GetClassHandler, Depends(get_get_class)],
) -> ClassOut:
    return _class_out(await handler.handle(person_id, class_id))


@router.post(
    "/{class_id}/materials",
    status_code=status.HTTP_201_CREATED,
    summary="Subir contenido de la clase (texto o PDF)",
    responses={**TEACHER_ONLY, 422: problem("Falta `text` o `file`, o el PDF es ilegible.")},
)
async def upload_class_material(
    class_id: UUID,
    _: CurrentPersonId,
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
async def invite_students(
    class_id: UUID,
    body: InvitationsRequest,
    person_id: CurrentPersonId,
    handler: Annotated[InviteStudentsHandler, Depends(get_invite_students)],
) -> list[MemberOut]:
    invited = await handler.handle(person_id, class_id, body.aliases)
    return [_member_out(m) for m in invited]


@router.get(
    "/{class_id}/members",
    summary="Código y lista de miembros con su estado",
    responses=TEACHER_ONLY,
)
async def list_members(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[ListMembersHandler, Depends(get_list_members)],
) -> MembersOut:
    view = await handler.handle(person_id, class_id)
    return MembersOut(invite_code=view.invite_code, members=[_member_out(m) for m in view.members])


@router.get("/{class_id}/dashboard", summary="Panel docente", responses=TEACHER_ONLY)
async def get_dashboard(class_id: UUID, _: CurrentPersonId) -> DashboardOut:
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
async def get_student(class_id: UUID, person_id: UUID, _: CurrentPersonId) -> StudentDetailOut:
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
