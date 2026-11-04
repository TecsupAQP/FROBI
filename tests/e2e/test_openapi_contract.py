"""The committed openapi.json is the contract with the front: it must match the code."""

from pathlib import Path

from frobi.openapi import render

CONTRACT = Path(__file__).resolve().parents[2] / "openapi.json"


def test_committed_openapi_matches_the_code() -> None:
    assert CONTRACT.exists(), "Run `uv run python -m frobi.openapi` and commit openapi.json"
    assert CONTRACT.read_text(encoding="utf-8") == render(), (
        "The API contract changed. If it is intentional, run `uv run python -m frobi.openapi`, "
        "commit openapi.json and tell the front."
    )
