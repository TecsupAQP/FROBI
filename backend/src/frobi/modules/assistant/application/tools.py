"""The lookups the assistant may make, per role. Each one is bound to the person asking."""

from uuid import UUID

from frobi.modules.assistant.application.ports import (
    AssistantTool,
    JsonObject,
    StudyData,
    ToolFailed,
)

NO_INPUT: JsonObject = {"type": "object", "properties": {}, "additionalProperties": False}
# Topics are already small (materials keeps them under ~6 000 characters); this only guards
# older materials whose single topic is the whole text.
MAX_GUIDE_CHARS = 30_000


def _uuid(arguments: JsonObject, name: str) -> UUID:
    value = arguments.get(name)
    if not isinstance(value, str):
        raise ToolFailed(f"Falta `{name}`.")
    try:
        return UUID(value)
    except ValueError as error:
        raise ToolFailed(f"`{name}` no es un id válido.") from error


def _topic(arguments: JsonObject) -> int:
    try:
        return int(arguments["topic"])
    except (TypeError, ValueError) as error:
        raise ToolFailed("`topic` debe ser el número del tema.") from error


def _guide_tools(data: StudyData, person_id: UUID, open_guide: UUID | None) -> list[AssistantTool]:
    async def list_guides(_: JsonObject) -> JsonObject:
        return {"guides": await data.guides(person_id)}

    async def read_guide(arguments: JsonObject) -> JsonObject:
        material_id = _uuid(arguments, "material_id") if "material_id" in arguments else open_guide
        if material_id is None:
            raise ToolFailed("No hay una guía abierta. Pide el id con list_my_guides.")
        guide = await data.guide(person_id, material_id)
        if guide is None:
            raise ToolFailed("No existe esa guía o la persona no puede verla.")
        topics: list[JsonObject] = list(guide.get("topics", []))
        if "topic" not in arguments and len(topics) > 1:
            # The table of contents first: reading one topic costs far fewer tokens than all.
            return {
                "id": guide["id"],
                "title": guide["title"],
                "topics": [{k: v for k, v in t.items() if k != "text"} for t in topics],
                "note": "Pide el tema que necesites con read_guide y topic.",
            }
        wanted = _topic(arguments) if "topic" in arguments else 1
        topic = next((t for t in topics if t.get("topic") == wanted), None)
        if topic is None:
            raise ToolFailed(f"La guía no tiene el tema {wanted}.")
        text = str(topic.get("text", ""))
        result: JsonObject = {"id": guide["id"], "title": guide["title"], **topic}
        if len(text) > MAX_GUIDE_CHARS:
            result["text"] = text[:MAX_GUIDE_CHARS]
            result["note"] = (
                f"Texto recortado: van los primeros {MAX_GUIDE_CHARS} de {len(text)} caracteres."
            )
        return result

    return [
        AssistantTool(
            name="list_my_guides",
            description="Lists the guides this person can study: the ones they uploaded or "
            "pasted, their class's content and FROBI's samples, with id, title and a preview.",
            input_schema=NO_INPUT,
            status="Buscando tus guías…",
            run=list_guides,
        ),
        AssistantTool(
            name="read_guide",
            description="Reads a guide. Without topic it returns its table of contents (topics "
            "with number, title and pages); with topic, the text of that topic. Without "
            "material_id it uses the guide the person has open. Read only the topics you need "
            "to answer, and quote them.",
            input_schema={
                "type": "object",
                "properties": {
                    "material_id": {
                        "type": "string",
                        "description": "Guide id from list_my_guides. Omit for the open guide.",
                    },
                    "topic": {
                        "type": "integer",
                        "description": "Topic number from the table of contents.",
                    },
                },
                "additionalProperties": False,
            },
            status="Leyendo la guía…",
            run=read_guide,
        ),
    ]


def learner_tools(data: StudyData, person_id: UUID, open_guide: UUID | None) -> list[AssistantTool]:
    async def my_progress(_: JsonObject) -> JsonObject:
        return await data.progress(person_id)

    return [
        *_guide_tools(data, person_id, open_guide),
        AssistantTool(
            name="my_progress",
            description="This person's own activity and performance: formats used, correct "
            "answers per format, prompt scores over time (out of 16), tasks solved without AI, "
            "autonomy level (1-3) and favorite format. Use it for summaries of how they are doing.",
            input_schema=NO_INPUT,
            status="Revisando tu progreso…",
            run=my_progress,
        ),
    ]


def teacher_tools(data: StudyData, person_id: UUID, open_guide: UUID | None) -> list[AssistantTool]:
    async def my_classes(_: JsonObject) -> JsonObject:
        return {"classes": await data.my_classes(person_id)}

    async def class_dashboard(arguments: JsonObject) -> JsonObject:
        panel = await data.class_panel(person_id, _uuid(arguments, "class_id"))
        if panel is None:
            raise ToolFailed("No existe esa clase o no es de este docente.")
        return panel

    async def student_detail(arguments: JsonObject) -> JsonObject:
        detail = await data.student(
            person_id, _uuid(arguments, "class_id"), _uuid(arguments, "student_id")
        )
        if detail is None:
            raise ToolFailed("Esa persona no es parte de esta clase.")
        return detail

    class_id: JsonObject = {"type": "string", "description": "Class id from my_classes."}
    return [
        *_guide_tools(data, person_id, open_guide),
        AssistantTool(
            name="my_classes",
            description="Lists the classes this teacher teaches: id, name, subject, tasks and "
            "invite code.",
            input_schema=NO_INPUT,
            status="Buscando tus clases…",
            run=my_classes,
        ),
        AssistantTool(
            name="class_dashboard",
            description="Teacher panel of one class, counting only activity done inside it: "
            "each student's progress and alerts (stuck on hint 1, needs review, not started), "
            "most used formats, most failed questions, help requests and tasks solved without "
            "AI. sample_data=true means it is example data, not real activity.",
            input_schema={
                "type": "object",
                "properties": {"class_id": class_id},
                "required": ["class_id"],
                "additionalProperties": False,
            },
            status="Revisando el panel de la clase…",
            run=class_dashboard,
        ),
        AssistantTool(
            name="student_detail",
            description="Detail of one student in the teacher's class: preferred format, "
            "correct answers, help requested per ladder step, tasks solved without AI and most "
            "failed question.",
            input_schema={
                "type": "object",
                "properties": {
                    "class_id": class_id,
                    "student_id": {
                        "type": "string",
                        "description": "person_id of the student, from class_dashboard.",
                    },
                },
                "required": ["class_id", "student_id"],
                "additionalProperties": False,
            },
            status="Revisando al estudiante…",
            run=student_detail,
        ),
    ]
