from frobi.shared.domain import DomainError, ErrorKind


class LanguageNotAvailable(DomainError):
    code = "Settings.LanguageNotAvailable"
    kind = ErrorKind.VALIDATION
    default_message = "Ese idioma todavía no está disponible. Por ahora solo hay español."


class UnknownSetting(DomainError):
    code = "Settings.UnknownSetting"
    kind = ErrorKind.VALIDATION
    default_message = "Ese ajuste no existe."
