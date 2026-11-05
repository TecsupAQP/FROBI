from frobi.shared.domain import DomainError, ErrorKind


class InvalidAlias(DomainError):
    code = "Identity.InvalidAlias"
    kind = ErrorKind.VALIDATION
    default_message = "Escribe un alias de 1 a 40 caracteres."


class InvalidCareer(DomainError):
    code = "Identity.InvalidCareer"
    kind = ErrorKind.VALIDATION
    default_message = "Escribe tu carrera (hasta 80 caracteres)."


class InvalidClassCode(DomainError):
    """The class code typed when entering does not match any class. Entering without it works."""

    code = "Classrooms.InvalidCode"
    kind = ErrorKind.VALIDATION
    default_message = "Ese código de clase no existe. Puedes entrar sin clase y unirte después."


class DemoUnavailable(DomainError):
    """The demo sign-in only exists with FROBI_ENVIRONMENT=local or demo."""

    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "El acceso demo no está disponible aquí."


class DemoNotSeeded(DomainError):
    code = "Identity.DemoNotSeeded"
    kind = ErrorKind.CONFLICT
    default_message = "Faltan los datos de demo. Córrelos con: uv run python -m frobi.demo"
