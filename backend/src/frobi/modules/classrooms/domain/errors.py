from frobi.shared.domain import DomainError, ErrorKind


class InvalidClassCode(DomainError):
    code = "Classrooms.InvalidCode"
    kind = ErrorKind.VALIDATION
    default_message = "Ese código de clase no existe. Revisa con tu docente."


class ClassNotFound(DomainError):
    """Also for a class that exists but the person may not see (no leaks)."""

    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa clase."


class TeachersOnly(DomainError):
    code = "Identity.Forbidden"
    kind = ErrorKind.FORBIDDEN
    default_message = "Solo un docente puede hacer esto."


class InvalidClassData(DomainError):
    code = "Classrooms.InvalidData"
    kind = ErrorKind.VALIDATION
    default_message = "Revisa el nombre, la materia y las tareas de la clase."


class NotInAClass(DomainError):
    code = "Classrooms.NotInAClass"
    kind = ErrorKind.CONFLICT
    default_message = "No estás en ninguna clase."


class MissingClassContent(DomainError):
    code = "Classrooms.MissingContent"
    kind = ErrorKind.VALIDATION
    default_message = "Pega el texto o sube un PDF para la clase (solo uno de los dos)."


class InvalidGuidePlan(DomainError):
    code = "Classrooms.InvalidGuide"
    kind = ErrorKind.VALIDATION
    default_message = "Revisa el tipo de guía y sus tareas."


class GuideNotFound(DomainError):
    """The material is not content of this class."""

    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa guía en la clase."
