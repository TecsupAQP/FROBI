"""Scanned PDFs (pages that are only images): read with Claude, or 'unreadable' without it."""

import base64
import json
from io import BytesIO

import httpx
import pytest
from pypdf import PdfWriter

from frobi.modules.materials.domain import PdfUnreadable
from frobi.modules.materials.infrastructure import PypdfTextExtractor
from frobi.shared.infrastructure.llm import (
    AnthropicPdfTranscriber,
    DisabledPdfTranscriber,
    LlmUnavailable,
    build_pdf_transcriber,
)


def _blank_pdf(pages: int = 1) -> bytes:
    """Pages with no text layer, like a scan."""
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class FakeTranscriber:
    def __init__(self, text: str = "", fails: bool = False) -> None:
        self.text = text
        self.fails = fails
        self.calls = 0

    async def transcribe(self, data: bytes) -> str:
        self.calls += 1
        if self.fails:
            raise LlmUnavailable("down")
        return self.text


async def test_a_scan_is_read_by_the_transcriber() -> None:
    reader = FakeTranscriber("## Motores\nUn motor convierte energía eléctrica en movimiento.")

    text = await PypdfTextExtractor(reader).extract(_blank_pdf())

    assert text.startswith("## Motores")
    assert reader.calls == 1


async def test_without_a_transcriber_or_when_it_fails_the_scan_stays_empty() -> None:
    failing = FakeTranscriber(fails=True)

    assert (await PypdfTextExtractor().extract(_blank_pdf())).strip() == ""
    assert (await PypdfTextExtractor(failing).extract(_blank_pdf())).strip() == ""
    assert failing.calls == 1


async def test_a_long_scan_is_refused_before_calling_the_ai() -> None:
    reader = FakeTranscriber("texto")

    with pytest.raises(PdfUnreadable, match="21 páginas"):
        await PypdfTextExtractor(reader).extract(_blank_pdf(21))
    assert reader.calls == 0


def _transport(body: object, seen: list[httpx.Request], status: int = 200) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status, json=body)

    return httpx.MockTransport(handle)


async def test_claude_receives_the_pdf_as_a_document_and_returns_its_text() -> None:
    seen: list[httpx.Request] = []
    reply = {"content": [{"type": "text", "text": "## Tema 1\nTexto de la guía."}]}
    reader = AnthropicPdfTranscriber(api_key="k", model="m", transport=_transport(reply, seen))
    pdf = _blank_pdf()

    text = await reader.transcribe(pdf)

    sent = json.loads(seen[0].content)
    document, instruction = sent["messages"][0]["content"]
    assert text == "## Tema 1\nTexto de la guía."
    assert document["type"] == "document"
    assert document["source"]["media_type"] == "application/pdf"
    assert base64.standard_b64decode(document["source"]["data"]) == pdf
    assert instruction["type"] == "text"
    assert sent["model"] == "m"


async def test_claude_says_there_is_no_text_or_fails() -> None:
    seen: list[httpx.Request] = []
    empty = AnthropicPdfTranscriber(
        api_key="k",
        transport=_transport({"content": [{"type": "text", "text": "SIN_TEXTO"}]}, seen),
    )
    down = AnthropicPdfTranscriber(api_key="k", transport=_transport({}, seen, status=529))

    assert await empty.transcribe(_blank_pdf()) == ""
    with pytest.raises(LlmUnavailable):
        await down.transcribe(_blank_pdf())


def test_only_anthropic_with_a_key_reads_scans() -> None:
    def build(provider: str, key: str | None) -> object:
        return build_pdf_transcriber(
            provider=provider, api_key=key, model=None, base_url=None, timeout_seconds=90
        )

    assert isinstance(build("anthropic", "k"), AnthropicPdfTranscriber)
    assert isinstance(build("anthropic", None), DisabledPdfTranscriber)
    assert isinstance(build("openai", "k"), DisabledPdfTranscriber)
