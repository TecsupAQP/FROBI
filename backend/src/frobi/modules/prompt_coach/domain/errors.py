from frobi.shared.domain import DomainError, ErrorKind


class EmptyPrompt(DomainError):
    code = "PromptCoach.EmptyPrompt"
    kind = ErrorKind.VALIDATION
    default_message = "Escribe la instrucción que le darías a la IA."


class EvaluationNotFound(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa evaluación."


class MaterialNotAvailable(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos ese material."
