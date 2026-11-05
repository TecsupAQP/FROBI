"""``StudyData`` over other modules' public APIs, so each one keeps enforcing its own rules:
a person only reads their own material and progress, a teacher only their own classes."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import classrooms, identity, materials, progress, settings
from frobi.modules.assistant.application.ports import JsonObject, PersonContext
from frobi.shared.domain import DomainError, ErrorKind

PREVIEW_CHARS = 160
# Preferences that change how the assistant should write.
READING_PREFERENCES = {"short_texts", "large_text", "voice", "reading", "attention", "low_vision"}


def _denied(error: DomainError) -> bool:
    return error.kind in (ErrorKind.NOT_FOUND, ErrorKind.FORBIDDEN)


class StudyDataAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def person(self, person_id: UUID) -> PersonContext | None:
        person = await identity.read_person_handler(self._session).find(person_id)
        if person is None:
            return None
        active = await classrooms.active_class_handler(self._session).handle(person_id)
        prefs = await settings.get_settings_handler(self._session).handle(person_id)
        chosen = {*prefs.profiles, *prefs.enabled_in_order()}
        return PersonContext(
            alias=person.alias,
            is_teacher=person.role is identity.Role.TEACHER,
            career=person.career,
            class_name=None if active is None else active.class_name,
            preferences=tuple(sorted(chosen & READING_PREFERENCES)),
        )

    async def guides(self, person_id: UUID) -> list[JsonObject]:
        found = await materials.guides_handler(self._session).for_person(person_id)
        return [
            {
                "id": str(m.id),
                "title": m.title,
                "origin": m.source.value,
                "is_class_content": m.kind is materials.MaterialKind.CLASS_CONTENT,
                "preview": m.preview(PREVIEW_CHARS),
            }
            for m in found
        ]

    async def guide(self, person_id: UUID, material_id: UUID) -> JsonObject | None:
        material = await materials.get_material_handler(self._session).find(person_id, material_id)
        if material is None:
            return None
        return {"id": str(material.id), "title": material.title, "text": material.text}

    async def progress(self, person_id: UUID) -> JsonObject:
        now = await progress.progress_handler(self._session).handle(person_id)
        journey = await progress.journey_handler(self._session).handle(person_id)
        recipe = journey.learned_recipe
        return {
            "has_data": now.has_data,
            "summary": now.message,
            "formats_used": [{"format": f, "count": n} for f, n in now.formats_used],
            "accuracy_by_format": [
                {"format": a.format, "correct": a.correct, "total": a.total}
                for a in now.accuracy_by_format
            ],
            "prompt_scores_out_of_16": [
                {"at": at.isoformat(), "total": total} for at, total in now.prompt_scores
            ],
            "solved_without_ai": now.solved_without_ai,
            "favorite_format": journey.favorite_format,
            "best_prompt_score": journey.best_prompt_score,
            "autonomy_level_1_to_3": journey.autonomy_level,
            "learned_recipe": None
            if recipe is None
            else {
                "context": recipe.context,
                "goal": recipe.goal,
                "level": recipe.level,
                "format": recipe.format,
            },
            "closing_message": journey.message,
        }

    async def my_classes(self, teacher_id: UUID) -> list[JsonObject]:
        try:
            found = await classrooms.my_classes_handler(self._session).handle(teacher_id)
        except DomainError as error:
            if _denied(error):
                return []
            raise
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "subject": c.subject,
                "tasks": list(c.tasks),
                "invite_code": c.invite_code,
            }
            for c in found
        ]

    async def class_panel(self, teacher_id: UUID, class_id: UUID) -> JsonObject | None:
        try:
            panel = await classrooms.dashboard_handler(self._session).handle(teacher_id, class_id)
        except DomainError as error:
            if _denied(error):
                return None
            raise
        return {
            "class_id": str(panel.class_id),
            "sample_data": panel.sample_data,
            "students": [
                {
                    "person_id": str(s.person_id),
                    "alias": s.alias,
                    "progress": s.progress_label,
                    "alerts": [a.text for a in s.alerts],
                }
                for s in panel.students
            ],
            "top_formats": [{"format": f, "count": n} for f, n in panel.top_formats],
            "most_failed_questions": [
                {"statement": q.statement, "fail_rate": q.fail_rate}
                for q in panel.most_failed_questions
            ],
            "help_requests": panel.help_requests,
            "solved_without_ai": panel.solved_without_ai,
        }

    async def student(
        self, teacher_id: UUID, class_id: UUID, student_id: UUID
    ) -> JsonObject | None:
        try:
            detail = await classrooms.student_detail_handler(self._session).handle(
                teacher_id, class_id, student_id
            )
        except DomainError as error:
            if _denied(error):
                return None
            raise
        return {
            "person_id": str(detail.person_id),
            "alias": detail.alias,
            "preferred_format": detail.preferred_format,
            "correct_answers": detail.correct_answers,
            "total_answers": detail.total_answers,
            "help_by_step": [{"step": s, "count": n} for s, n in detail.help_by_step],
            "solved_without_ai": detail.solved_without_ai,
            "most_failed_question": detail.most_failed_question,
        }
