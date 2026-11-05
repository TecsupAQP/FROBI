"""What the person reads when the AI cannot answer (RNF03: FROBI never leaves them stuck)."""

UNAVAILABLE = (
    "Ahora no puedo responder con IA, pero FROBI sigue funcionando. Algunas ideas:\n"
    "- Para estudiar, ve a «Inicio y mis guías», abre una guía y elige un formato.\n"
    "- Si te trabas en una tarea, usa la «Escalera de ayuda»: pistas antes de la respuesta.\n"
    "- Para ver cómo vas, entra a «Mi progreso».\n"
    "- «Cómo se usa FROBI», en el menú, explica cada pantalla.\n"
    "Vuelve a preguntarme en un rato."
)

TEACHER_UNAVAILABLE = (
    "Ahora no puedo responder con IA, pero FROBI sigue funcionando. Algunas ideas:\n"
    "- En «Panel docente» ves el avance y las alertas de cada estudiante.\n"
    "- Desde «Crear clase» subes el contenido y en «Invitar alumnos» compartes el código.\n"
    "- «Cómo se usa FROBI», en el menú, explica cada pantalla.\n"
    "Vuelve a preguntarme en un rato."
)

INTERRUPTED = "\n\n(No pude terminar esta respuesta. Vuelve a preguntarme en un rato.)"


def unavailable_for(is_teacher: bool) -> str:
    return TEACHER_UNAVAILABLE if is_teacher else UNAVAILABLE
