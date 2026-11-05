"""Guías de la clase: cómo se estudia cada material que sube el docente y cuánto avanzó cada alumno.

- Guía de estudio: no tiene tareas; el alumno la estudia y al final la IA lo evalúa con
  preguntas. Su avance es el resultado de la última evaluación (aciertos sobre el total).
- Guía con tareas: el docente escribe 1 a 20 tareas. Una tarea está hecha cuando el alumno dejó
  su propio intento en la escalera de ayuda. Su avance es tareas hechas sobre el total.
"""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import InvalidGuidePlan

MAX_TASKS = 20
MAX_TASK_LENGTH = 500


class GuideMode(StrEnum):
    STUDY = "study"
    TASKS = "tasks"


@dataclass(frozen=True, slots=True)
class GuideTask:
    id: UUID
    position: int
    statement: str


@dataclass(frozen=True, slots=True)
class GuidePlan:
    material_id: UUID
    class_id: UUID
    mode: GuideMode
    tasks: tuple[GuideTask, ...]

    @classmethod
    def create(
        cls,
        material_id: UUID,
        class_id: UUID,
        mode: GuideMode,
        statements: list[str],
        existing: tuple[GuideTask, ...] = (),
    ) -> "GuidePlan":
        """``existing`` keeps the ids of unchanged tasks, so progress survives edits."""
        cleaned = list(dict.fromkeys(t for t in (" ".join(s.split()) for s in statements) if t))
        if mode is GuideMode.STUDY and cleaned:
            raise InvalidGuidePlan("Una guía de estudio no tiene tareas: la evalúa la IA al final.")
        if mode is GuideMode.TASKS and not cleaned:
            raise InvalidGuidePlan("Escribe al menos una tarea para esta guía.")
        if len(cleaned) > MAX_TASKS or any(len(t) > MAX_TASK_LENGTH for t in cleaned):
            raise InvalidGuidePlan(
                f"Hasta {MAX_TASKS} tareas por guía, de {MAX_TASK_LENGTH} caracteres o menos."
            )
        previous = {task.statement: task.id for task in existing}
        tasks = tuple(
            GuideTask(previous.get(text, uuid4()), position, text)
            for position, text in enumerate(cleaned, start=1)
        )
        return cls(material_id, class_id, mode, tasks)

    @classmethod
    def default(cls, material_id: UUID, class_id: UUID) -> "GuidePlan":
        """Material uploaded before guides had a type: a study guide."""
        return cls(material_id, class_id, GuideMode.STUDY, ())


def task_ref_of(task_id: UUID) -> str:
    """The ``task_ref`` the help ladder records for a task of a guide."""
    return f"tarea-{task_id}"


@dataclass(frozen=True, slots=True)
class GuideProgress:
    material_id: UUID
    mode: GuideMode
    completion: int
    done_task_ids: tuple[UUID, ...]
    # (aciertos, preguntas) de la última evaluación respondida; None si aún no hay.
    evaluation: tuple[int, int] | None
