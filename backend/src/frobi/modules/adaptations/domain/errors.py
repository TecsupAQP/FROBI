from frobi.shared.domain import DomainError, ErrorKind


class MaterialNotAvailable(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos ese material."


class AdaptationNotFound(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos esa adaptación."
