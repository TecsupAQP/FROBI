"""Public API of progress: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from .application import GetJourneySummaryHandler, GetProgressHandler, JourneySummary, Progress


def progress_handler(session: AsyncSession) -> GetProgressHandler:
    """The person's own progress (``/me/progress``), inside or outside a class."""
    from .infrastructure import PersonActivityReaderAdapter

    return GetProgressHandler(PersonActivityReaderAdapter(session))


def journey_handler(session: AsyncSession) -> GetJourneySummaryHandler:
    """The person's closing summary (``/me/journey-summary``)."""
    from .infrastructure import PersonActivityReaderAdapter

    return GetJourneySummaryHandler(PersonActivityReaderAdapter(session))


__all__ = [
    "GetJourneySummaryHandler",
    "GetProgressHandler",
    "JourneySummary",
    "Progress",
    "journey_handler",
    "progress_handler",
]
