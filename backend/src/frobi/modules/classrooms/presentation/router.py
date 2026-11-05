"""M12 · Clase del docente.

Real: create a class, list my classes, join with a code, see the class, invite, list members.
Real: the teacher panel and the student detail, both only with activity of this class.
Real: class content uploaded by the teacher, read by the teacher and joined students.
Real: each class material is a study guide (final evaluation) or a guide with tasks, and both
the student and the teacher see its completion percentage.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from frobi.modules.classrooms.application import (
    ClassGuide,
    ClassGuidesProgressHandler,
    CreateClassCommand,
    CreateClassHandler,
    DashboardHandler,
    GetClassHandler,
    InviteStudentsHandler,
    JoinWithCodeHandler,
    ListClassGuidesHandler,
    ListMembersHandler,
    ListMyClassesHandler,
    MyGuidesProgressHandler,
    SaveGuidePlanCommand,
    SaveGuidePlanHandler,
    StudentDetailHandler,
    UploadClassContentCommand,
    UploadClassContentHandler,
)
from frobi.modules.classrooms.domain import (
    Classroom,
    GuideMode,
    GuidePlan,
    GuideProgress,
    Membership,
    task_ref_of,
)
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    TEACHER_RESPONSES,
    CurrentPersonId,
    problem,
)

from .dependencies import (
    get_class_guides_progress,
    get_create_class,
    get_get_class,
    get_invite_students,
    get_join_class,
    get_list_class_guides,
    get_list_members,
    get_list_my_classes,
    get_my_guides_progress,
    get_save_guide_plan,
    get_student_detail,
    get_upload_class_content,
)
from .dependencies import (
    get_dashboard as get_dashboard_handler,
)
from .schemas import (
    AiUsage,
    Alert,
    ClassMaterialOut,
    ClassMaterialSummaryOut,
    ClassOut,
    CreateClassRequest,
    DashboardOut,
    EvaluationOut,
    FailedQuestion,
    FormatCount,
    GuideClassProgressOut,
    GuidePlanOut,
    GuidePlanRequest,
    GuideProgressOut,
    GuideTaskOut,
    HelpByStep,
    InvitationsRequest,
    JoinClassOut,
    JoinClassRequest,
    MemberOut,
    MembersOut,
    StudentDetailOut,
    StudentGuideProgressOut,
    StudentRow,
)

router = APIRouter(prefix="/classes", tags=["M12 · Clase del docente"], responses=AUTH_RESPONSES)


def _tasks_out(plan: GuidePlan) -> list[GuideTaskOut]:
    return [
        GuideTaskOut(
            id=task.id,
            position=task.position,
            statement=task.statement,
            task_ref=task_ref_of(task.id),
        )
        for task in plan.tasks
    ]


def _progress_out(progress: GuideProgress) -> GuideProgressOut:
    evaluation = progress.evaluation
    return GuideProgressOut(
        material_id=progress.material_id,
        mode=progress.mode,
        completion=progress.completion,
        done_task_ids=list(progress.done_task_ids),
        evaluation=(
            None
            if evaluation is None
            else EvaluationOut(correct=evaluation[0], total=evaluation[1])
        ),
    )


TEACHER_ONLY = {**TEACHER_RESPONSES, **NOT_FOUND_RESPONSES}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


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


@router.get(
    "",
    summary="Mis clases (docente)",
    description="Las clases que enseña la persona actual, la más reciente primero.",
    responses=TEACHER_RESPONSES,
)
async def list_my_classes(
    person_id: CurrentPersonId,
    handler: Annotated[ListMyClassesHandler, Depends(get_list_my_classes)],
) -> list[ClassOut]:
    return [_class_out(c) for c in await handler.handle(person_id)]


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
    description=(
        "Solo el docente de la clase. Envía `text` o `file` (PDF de hasta 10 MB), no los dos. "
        "Los estudiantes unidos a la clase lo ven en `GET /classes/{id}/materials` y lo usan "
        "como cualquier material (`GET /materials/{id}`, adaptaciones, revisión de afirmaciones). "
        "Con `mode=tasks` envía las tareas como varios campos `tasks`."
    ),
    responses={
        **TEACHER_ONLY,
        422: problem(
            "Falta `text` o `file`, o vienen los dos (`Classrooms.MissingContent`); PDF ilegible "
            "(`Materials.PdfUnreadable`) o de más de 10 MB (`Materials.FileTooLarge`)."
        ),
    },
)
async def upload_class_material(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[UploadClassContentHandler, Depends(get_upload_class_content)],
    title: Annotated[str, Form(min_length=1, max_length=120)],
    save_plan: Annotated[SaveGuidePlanHandler, Depends(get_save_guide_plan)],
    text: Annotated[str | None, Form(max_length=100_000)] = None,
    file: Annotated[UploadFile | None, File(description="PDF de hasta 10 MB.")] = None,
    mode: Annotated[
        GuideMode, Form(description="`study` (por defecto) o `tasks`.")
    ] = GuideMode.STUDY,
    tasks: Annotated[
        list[str] | None, Form(description="Enunciados de las tareas (solo con `mode=tasks`).")
    ] = None,
) -> ClassMaterialOut:
    # Read one byte past the limit so a huge upload is rejected without loading it all.
    pdf = None if file is None else await file.read(MAX_UPLOAD_BYTES + 1)
    material = await handler.handle(
        UploadClassContentCommand(
            teacher_id=person_id, class_id=class_id, title=title, text=text, pdf=pdf
        )
    )
    plan = await save_plan.handle(
        SaveGuidePlanCommand(
            teacher_id=person_id,
            class_id=class_id,
            material_id=material.id,
            mode=mode,
            tasks=tasks or [],
        )
    )
    return ClassMaterialOut(
        id=material.id,
        class_id=material.class_id,
        title=material.title,
        extracted_text=material.text,
        mode=plan.mode,
        tasks=_tasks_out(plan),
    )


@router.get(
    "/{class_id}/materials",
    summary="Contenido de la clase",
    description="El docente de la clase y sus estudiantes unidos. El más reciente primero.",
    responses=NOT_FOUND_RESPONSES,
)
async def list_class_materials(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[ListClassGuidesHandler, Depends(get_list_class_guides)],
) -> list[ClassMaterialSummaryOut]:
    return [_summary(guide) for guide in await handler.handle(person_id, class_id)]


def _summary(guide: ClassGuide) -> ClassMaterialSummaryOut:
    material = guide.material
    return ClassMaterialSummaryOut(
        id=material.id,
        class_id=material.class_id,
        title=material.title,
        preview=material.preview,
        created_at=material.created_at,
        mode=guide.plan.mode,
        tasks=_tasks_out(guide.plan),
    )


@router.put(
    "/{class_id}/materials/{material_id}/guide",
    summary="Definir si una guía es de estudio o tiene tareas",
    description=(
        "Solo el docente de la clase. `study`: sin tareas, la IA evalúa al final. `tasks`: 1 a "
        "20 tareas. Las tareas que no cambian conservan su id (y el avance de los alumnos)."
    ),
    responses={
        **TEACHER_ONLY,
        422: problem("Tipo de guía y tareas incompatibles (`Classrooms.InvalidGuide`)."),
    },
)
async def save_guide_plan(
    class_id: UUID,
    material_id: UUID,
    body: GuidePlanRequest,
    person_id: CurrentPersonId,
    handler: Annotated[SaveGuidePlanHandler, Depends(get_save_guide_plan)],
) -> GuidePlanOut:
    plan = await handler.handle(
        SaveGuidePlanCommand(
            teacher_id=person_id,
            class_id=class_id,
            material_id=material_id,
            mode=body.mode,
            tasks=body.tasks,
        )
    )
    return GuidePlanOut(material_id=plan.material_id, mode=plan.mode, tasks=_tasks_out(plan))


@router.get(
    "/{class_id}/guides/my-progress",
    summary="Mi avance en cada guía de la clase",
    description=(
        "Guía con tareas: tareas con intento propio sobre el total. Guía de estudio: resultado "
        "de la última evaluación final respondida. Solo cuenta lo hecho dentro de la clase."
    ),
    responses=NOT_FOUND_RESPONSES,
)
async def my_guides_progress(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[MyGuidesProgressHandler, Depends(get_my_guides_progress)],
) -> list[GuideProgressOut]:
    return [_progress_out(progress) for progress in await handler.handle(person_id, class_id)]


@router.get(
    "/{class_id}/guides/progress",
    summary="Avance de cada alumno en cada guía (docente)",
    description="Solo el docente de la clase. Detecta a tiempo quién se traba; no califica.",
    responses=TEACHER_ONLY,
)
async def class_guides_progress(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[ClassGuidesProgressHandler, Depends(get_class_guides_progress)],
) -> list[GuideClassProgressOut]:
    return [
        GuideClassProgressOut(
            material_id=item.guide.material.id,
            title=item.guide.material.title,
            mode=item.guide.plan.mode,
            tasks_total=len(item.guide.plan.tasks),
            students=[
                StudentGuideProgressOut(
                    person_id=student.person_id,
                    alias=student.alias,
                    completion=student.progress.completion,
                )
                for student in item.students
            ],
        )
        for item in await handler.handle(person_id, class_id)
    ]


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


@router.get(
    "/{class_id}/dashboard",
    summary="Panel docente (solo actividad hecha dentro de la clase)",
    responses=TEACHER_ONLY,
)
async def get_dashboard(
    class_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[DashboardHandler, Depends(get_dashboard_handler)],
) -> DashboardOut:
    panel = await handler.handle(person_id, class_id)
    return DashboardOut(
        class_id=panel.class_id,
        sample_data=panel.sample_data,
        students=[
            StudentRow(
                person_id=s.person_id,
                alias=s.alias,
                progress_label=s.progress_label,
                alerts=[Alert(code=a.code, text=a.text, icon=a.icon) for a in s.alerts],
            )
            for s in panel.students
        ],
        top_formats=[FormatCount(format=f, count=n) for f, n in panel.top_formats],  # type: ignore[arg-type]
        most_failed_questions=[
            FailedQuestion(statement=q.statement, fail_rate=q.fail_rate)
            for q in panel.most_failed_questions
        ],
        ai_usage=AiUsage(
            help_requests=panel.help_requests, solved_without_ai=panel.solved_without_ai
        ),
    )


@router.get(
    "/{class_id}/students/{person_id}",
    summary="Detalle de un estudiante (solo actividad de esta clase)",
    responses=TEACHER_ONLY,
)
async def get_student(
    class_id: UUID,
    person_id: UUID,
    teacher_id: CurrentPersonId,
    handler: Annotated[StudentDetailHandler, Depends(get_student_detail)],
) -> StudentDetailOut:
    detail = await handler.handle(teacher_id, class_id, person_id)
    return StudentDetailOut(
        person_id=detail.person_id,
        alias=detail.alias,
        preferred_format=detail.preferred_format,  # type: ignore[arg-type]
        correct_answers=detail.correct_answers,
        total_answers=detail.total_answers,
        help_by_step=[HelpByStep(step=s, count=n) for s, n in detail.help_by_step],  # type: ignore[arg-type]
        solved_without_ai=detail.solved_without_ai,
        most_failed_question=detail.most_failed_question,
    )
