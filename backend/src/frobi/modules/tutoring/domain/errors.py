from frobi.shared.domain import DomainError, ErrorKind


class StepOutOfOrder(DomainError):
    code = "Tutoring.StepOutOfOrder"
    kind = ErrorKind.CONFLICT
    default_message = "Primero abre el escalón anterior."


class FinalLocked(DomainError):
    code = "Tutoring.FinalLocked"
    kind = ErrorKind.CONFLICT
    default_message = "Se desbloquea después de tu intento."


class AttemptNotFound(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos ese intento."


class AdaptationNotAvailable(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa adaptación."
