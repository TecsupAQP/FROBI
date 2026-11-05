"""PdfTextExtractor on pypdf. Parsing is CPU-bound, so it runs in a worker thread.

A scanned PDF has pages that are only images, so pypdf finds (almost) no text. Then, if there is
a ``PdfTranscriber`` (Claude), it reads the page images; if it fails or there is none, the text
stays empty and the upload answers "unreadable" as before.
"""

import asyncio
import logging
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from frobi.modules.materials.domain import PdfUnreadable
from frobi.shared.infrastructure.llm import LlmUnavailable, PdfTranscriber

logger = logging.getLogger(__name__)

MAX_PAGES = 200
# Reading images is slow and costs tokens per page: scans up to this many pages.
MAX_SCANNED_PAGES = 20
# Fewer visible characters per page than this means the pages are images (a scan).
MIN_CHARS_PER_PAGE = 25


def _read(data: bytes) -> tuple[str, int]:
    """The text layer and the number of pages."""
    if not data.lstrip()[:5].startswith(b"%PDF"):
        raise PdfUnreadable()
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise PdfUnreadable("Ese PDF tiene contraseña. Quítala o pega el texto.")
        pages = reader.pages[:MAX_PAGES]
        return "\n\n".join(page.extract_text() or "" for page in pages), len(reader.pages)
    except PdfUnreadable:
        raise
    except (PyPdfError, ValueError, KeyError, TypeError, OSError) as error:
        raise PdfUnreadable() from error


def looks_scanned(text: str, pages: int) -> bool:
    visible = len("".join(text.split()))
    return visible < MIN_CHARS_PER_PAGE * max(pages, 1)


class PypdfTextExtractor:
    def __init__(self, transcriber: PdfTranscriber | None = None) -> None:
        self._transcriber = transcriber

    async def extract(self, data: bytes) -> str:
        text, pages = await asyncio.to_thread(_read, data)
        if self._transcriber is None or not looks_scanned(text, pages):
            return text
        if pages > MAX_SCANNED_PAGES:
            raise PdfUnreadable(
                f"Ese PDF es escaneado y tiene {pages} páginas. Leemos escaneos de hasta "
                f"{MAX_SCANNED_PAGES} páginas: divídelo o pega el texto."
            )
        try:
            transcript = await self._transcriber.transcribe(data)
        except LlmUnavailable:
            logger.warning("Scanned PDF of %s pages not transcribed", pages, exc_info=True)
            return text
        return transcript if len(transcript.strip()) > len(text.strip()) else text
