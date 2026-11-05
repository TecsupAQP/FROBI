"""Reading scanned PDFs (pages that are only images) with Claude.

The Anthropic Messages API accepts a PDF as a ``document`` block and reads both its text and its
page images, so a scan or a photographed handout becomes plain text. Only used when the PDF has no
text layer of its own; without an Anthropic key the upload keeps answering "unreadable".
"""

import base64
from typing import Any, Protocol

from .client import LlmUnavailable
from .providers import ANTHROPIC_URL, ANTHROPIC_VERSION, DEFAULT_ANTHROPIC_MODEL, _HttpLlmClient

# A dense page is ~800 tokens of text: room for the 20 pages we accept, with margin.
MAX_TRANSCRIPT_TOKENS = 20_000
NO_TEXT = "SIN_TEXTO"

SYSTEM = (
    "Eres un transcriptor de documentos de estudio. Copias el texto tal como aparece en el PDF, "
    "en su idioma original, sin resumir, sin corregir, sin traducir y sin agregar nada."
)
PROMPT = (
    "Transcribe todo el texto de este PDF, página por página y en orden de lectura.\n"
    "- Marca cada título o sección con una línea que empiece con '## '.\n"
    "- Escribe las tablas como líneas de texto, una fila por línea.\n"
    "- Describe una figura en una línea entre corchetes solo si tiene texto o datos.\n"
    "- No agregues comentarios, introducciones ni notas tuyas.\n"
    f"Si el PDF no tiene texto legible, responde solo: {NO_TEXT}"
)


class PdfTranscriber(Protocol):
    async def transcribe(self, data: bytes) -> str:
        """Plain text of the PDF read from its page images. Raises LlmUnavailable on failure."""
        ...


class DisabledPdfTranscriber:
    """Without an Anthropic key: scanned PDFs stay unreadable."""

    async def transcribe(self, data: bytes) -> str:
        raise LlmUnavailable("No PDF reader configured")


class AnthropicPdfTranscriber(_HttpLlmClient):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_ANTHROPIC_MODEL,
        base_url: str = ANTHROPIC_URL,
        timeout_seconds: float = 90.0,
        transport: Any = None,
    ) -> None:
        super().__init__(timeout_seconds=timeout_seconds, transport=transport)
        self._api_key = api_key
        self._model = model
        self._url = base_url.rstrip("/") + "/v1/messages"

    async def transcribe(self, data: bytes) -> str:
        document = base64.standard_b64encode(data).decode("ascii")
        reply = await self._post(
            self._url,
            {
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
            {
                "model": self._model,
                "max_tokens": MAX_TRANSCRIPT_TOKENS,
                "system": SYSTEM,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": document,
                                },
                            },
                            {"type": "text", "text": PROMPT},
                        ],
                    }
                ],
            },
        )
        try:
            text = "".join(
                block["text"] for block in reply["content"] if block.get("type") == "text"
            )
        except (KeyError, TypeError, AttributeError) as error:
            raise LlmUnavailable("Unexpected Anthropic reply") from error
        # A transcript cut at the token limit is still the start of the guide: keep it.
        text = text.strip()
        return "" if text == NO_TEXT else text


def build_pdf_transcriber(
    *,
    provider: str,
    api_key: str | None,
    model: str | None,
    base_url: str | None,
    timeout_seconds: float,
) -> PdfTranscriber:
    """Claude when the provider is Anthropic with a key; otherwise scans stay unreadable."""
    if provider != "anthropic" or not api_key:
        return DisabledPdfTranscriber()
    return AnthropicPdfTranscriber(
        api_key=api_key,
        model=model or DEFAULT_ANTHROPIC_MODEL,
        base_url=base_url or ANTHROPIC_URL,
        timeout_seconds=timeout_seconds,
    )
