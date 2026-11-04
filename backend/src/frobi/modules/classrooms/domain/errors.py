from frobi.shared.domain import DomainError, ErrorKind


class InvalidClassCode(DomainError):
    code = "Classrooms.InvalidCode"
    kind = ErrorKind.VALIDATION
    default_message = "Ese código de clase no existe. Revisa con tu docente."
