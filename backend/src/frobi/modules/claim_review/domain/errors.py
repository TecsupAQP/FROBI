from frobi.shared.domain import DomainError, ErrorKind


class WorkNotAvailable(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos ese trabajo."


class ReviewNotFound(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "Todavía no revisaste las afirmaciones de este trabajo."


class NothingToReview(DomainError):
    code = "ClaimReview.NothingToReview"
    kind = ErrorKind.VALIDATION
    default_message = "Tu borrador no tiene frases para revisar todavía."
