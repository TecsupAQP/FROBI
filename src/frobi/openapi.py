"""Write the OpenAPI contract the front consumes: ``uv run python -m frobi.openapi``."""

import json
import sys
from pathlib import Path
from typing import Any

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

DEFAULT_PATH = Path("openapi.json")


def render() -> str:
    # Fixed settings (no .env, no environment) so the contract is identical on every machine.
    app = create_app(Settings(_env_file=None))
    schema: dict[str, Any] = app.openapi()
    return json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    target.write_text(render(), encoding="utf-8")
    print(f"OpenAPI written to {target}")


if __name__ == "__main__":
    main()
