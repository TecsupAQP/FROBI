from frobi.shared.domain import DomainError, ErrorKind

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 200_000


class PdfUnreadable(DomainError):
    code = "Materials.PdfUnreadable"
    kind = ErrorKind.VALIDATION
    default_message = "No pudimos leer ese PDF. Prueba con otro archivo o pega el texto."


class FileTooLarge(DomainError):
    code = "Materials.FileTooLarge"
    kind = ErrorKind.VALIDATION
    default_message = "El archivo supera los 10 MB."


class EmptyText(DomainError):
    code = "Materials.EmptyText"
    kind = ErrorKind.VALIDATION
    default_message = "El material no tiene texto."


class InvalidTitle(DomainError):
    code = "Materials.InvalidTitle"
    kind = ErrorKind.VALIDATION
    default_message = "Escribe un título de 1 a 120 caracteres."


class WrongKind(DomainError):
    code = "Materials.WrongKind"
    kind = ErrorKind.VALIDATION
    default_message = (
        "La consigna debe ser un material de tipo `brief` y el borrador de tipo `draft`."
    )


class MaterialNotFound(DomainError):
    """Also used when the material exists but belongs to someone else (RNF08: no leaks)."""

    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos ese material."
