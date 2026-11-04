"""Base error for business rules.

Each subclass declares a stable ``code`` (``Module.Reason``) that the front switches on, and a
``kind`` that the presentation layer maps to an HTTP status. The domain never knows about HTTP.
"""

from enum import StrEnum
from typing import ClassVar


class ErrorKind(StrEnum):
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    UNAUTHENTICATED = "unauthenticated"
    FORBIDDEN = "forbidden"


class DomainError(Exception):
    code: ClassVar[str] = "Domain.Error"
    kind: ClassVar[ErrorKind] = ErrorKind.CONFLICT
    default_message: ClassVar[str] = "No se pudo completar la operación."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)
