"""Errors raised by use cases that are not tied to a single module's rules."""

from frobi.shared.domain import DomainError, ErrorKind


class NotFound(DomainError):
    code = "Resource.NotFound"
    kind = ErrorKind.NOT_FOUND
    default_message = "No encontramos lo que buscas."


class Unauthenticated(DomainError):
    code = "Identity.Unauthenticated"
    kind = ErrorKind.UNAUTHENTICATED
    default_message = "Necesitas entrar para continuar."


class Forbidden(DomainError):
    code = "Identity.Forbidden"
    kind = ErrorKind.FORBIDDEN
    default_message = "Tu rol no permite hacer esto."
