from frobi.shared.domain import DomainError, ErrorKind


class InvalidOption(DomainError):
    code = "Comprehension.InvalidOption"
    kind = ErrorKind.VALIDATION
    default_message = "Esa opción no existe en la pregunta."


class NotEnoughMaterial(DomainError):
    code = "Comprehension.NotEnoughMaterial"
    kind = ErrorKind.VALIDATION
    default_message = "Tu material es muy corto para armar preguntas. Agrega más texto."


class QuestionNotFound(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa pregunta."


class AdaptationNotAvailable(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa adaptación."


class InvalidQuestion(ValueError):
    """A generated question is malformed (programming or model error, never shown as-is)."""
