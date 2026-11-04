from frobi.shared.domain import DomainError, ErrorKind


class PdfUnreadable(DomainError):
    code = "Materials.PdfUnreadable"
    kind = ErrorKind.VALIDATION
    default_message = "No pudimos leer ese PDF. Prueba con otro archivo o pega el texto."


class FileTooLarge(DomainError):
    code = "Materials.FileTooLarge"
    kind = ErrorKind.VALIDATION
    default_message = "El archivo supera los 10 MB."


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
