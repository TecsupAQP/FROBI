"""Example guides shipped inside the package (``samples/*.md``), so Docker images carry them.

Each file's first ``# heading`` is its title. Ids are fixed so the front and the demo can link
to them.
"""

from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from uuid import UUID

from frobi.modules.materials.domain import Material, MaterialKind, MaterialSource, normalize_text

SAMPLES_DIR = Path(__file__).parent / "samples"
SAMPLE_IDS: dict[str, UUID] = {
    "sensores_industriales.md": UUID("00000000-0000-4000-8000-00000000a001"),
}
PUBLISHED_AT = datetime(2026, 11, 4, tzinfo=UTC)


def _load(path: Path, sample_id: UUID) -> Material:
    raw = path.read_text(encoding="utf-8")
    first, _, body = raw.partition("\n")
    return Material(
        id=sample_id,
        owner_id=None,
        class_id=None,
        title=first.lstrip("#").strip(),
        kind=MaterialKind.GUIDE,
        source=MaterialSource.SAMPLE,
        text=normalize_text(body),
        created_at=PUBLISHED_AT,
    )


@cache
def _all() -> tuple[Material, ...]:
    return tuple(_load(SAMPLES_DIR / name, sample_id) for name, sample_id in SAMPLE_IDS.items())


class FileSampleCatalog:
    def list(self) -> list[Material]:
        return list(_all())

    def get(self, material_id: UUID) -> Material | None:
        return next((m for m in _all() if m.id == material_id), None)
