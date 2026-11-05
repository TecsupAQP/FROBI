"""Build tiny but valid PDFs for tests (one page, Helvetica, ASCII text)."""


def make_pdf(*lines: str) -> bytes:
    commands = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
    for line in lines:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({escaped}) Tj T*")
    commands.append("ET")
    content = "\n".join(commands).encode("latin-1") if lines else b""

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return bytes(out)


def make_structured_pdf(
    pages: list[list[tuple[str, int]]], outline: list[tuple[str, int]] = ()
) -> bytes:
    """Several pages of (line, font size); ``outline`` adds bookmarks as (title, page index)."""
    from io import BytesIO

    from pypdf import PdfWriter

    contents = []
    for lines in pages:
        commands = ["BT", "72 740 Td"]
        for line, size in lines:
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            commands += [f"/F1 {size} Tf", f"{size + 4} TL", f"({escaped}) Tj T*"]
        commands.append("ET")
        contents.append("\n".join(commands).encode("latin-1"))

    count = len(pages)
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(count)).encode()
    font_number = 3 + 2 * count
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [" + kids + b"] /Count %d >>" % count,
    ]
    for i, content in enumerate(contents):
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents %d 0 R "
            b"/Resources << /Font << /F1 %d 0 R >> >> >>" % (4 + 2 * i, font_number)
        )
        objects.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    if not outline:
        return bytes(out)
    writer = PdfWriter(clone_from=BytesIO(bytes(out)))
    for title, page in outline:
        writer.add_outline_item(title, page)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()
