from frobi.shared.domain import DomainError, ErrorKind


class InvalidClassCode(DomainError):
    """The class code typed when entering does not match any class. Entering without it works."""

    code = "Classrooms.InvalidCode"
    kind = ErrorKind.VALIDATION
    default_message = "Ese código de clase no existe. Puedes entrar sin clase y unirte después."
