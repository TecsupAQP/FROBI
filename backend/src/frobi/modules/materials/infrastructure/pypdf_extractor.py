"""PdfTextExtractor on pypdf. Parsing is CPU-bound, so it runs in a worker thread."""

import asyncio
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from frobi.modules.materials.domain import PdfUnreadable

MAX_PAGES = 200


def _extract(data: bytes) -> str:
    if not data.lstrip()[:5].startswith(b"%PDF"):
        raise PdfUnreadable()
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise PdfUnreadable("Ese PDF tiene contraseña. Quítala o pega el texto.")
        pages = reader.pages[:MAX_PAGES]
        return "\n\n".join(page.extract_text() or "" for page in pages)
    except PdfUnreadable:
        raise
    except (PyPdfError, ValueError, KeyError, TypeError, OSError) as error:
        raise PdfUnreadable() from error


class PypdfTextExtractor:
    async def extract(self, data: bytes) -> str:
        return await asyncio.to_thread(_extract, data)
