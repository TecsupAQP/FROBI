from frobi.shared.domain import DomainError, ErrorKind


class NeedRequired(DomainError):
    code = "Tools.NeedRequired"
    kind = ErrorKind.VALIDATION
    default_message = "Dinos qué necesitas o elige una afirmación revisada."


class UnknownNeed(DomainError):
    code = "Tools.UnknownNeed"
    kind = ErrorKind.VALIDATION
    default_message = "Esa necesidad no está en el catálogo."


class ClaimNotAvailable(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa afirmación."
