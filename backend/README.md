# FROBI backend

Backend for FROBI (Hack4Edu 2026): FastAPI + PostgreSQL + Redis, organized as a hexagonal modular monolith.

> Status: Phase 0 done. Every endpoint of `PLAN_BACKEND.md` §6 exists under `/api/v1` with its
> final schema, but **module endpoints are stubs that return example data** (they keep no state).
> Phase 1 replaces them with the real use cases without changing the contract.

## Authentication

1. `POST /api/v1/sessions` with `{"alias": "Ana", "career": "Mecatrónica", "role": "learner"}`
   (optional `"class_code"`; the stub accepts `SENSOR1`, anything else is
   `422 Classrooms.InvalidCode`).
2. Send the returned token on every other call: `Authorization: Bearer <token>`.
   Without it you get `401 Identity.Unauthenticated`.

While the endpoints are stubs, any non-empty token is accepted. In `/docs`, use **Authorize**.

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs Python 3.12 for you)
- Docker Desktop (Postgres 16 and Redis 7)

## Local development

```bash
cp .env.example .env                                        # optional, defaults work locally
uv sync                                                     # dependencies into .venv
docker compose -f docker/compose.yml up -d postgres redis   # databases
uv run uvicorn frobi.main:create_app --factory --reload --reload-dir src  # API on http://localhost:8000
```

- Interactive docs: http://localhost:8000/docs (only while the API is running)
- Health: http://localhost:8000/api/v1/health → `{"status": "ok", "checks": {"postgres": "up", "redis": "up"}}`, or `503` with `"degraded"` if one is down

Everything in Docker, API included: `docker compose -f docker/compose.yml up --build`.

## Checks (same as CI)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run lint-imports        # architecture rules from ARCHITECTURE.md §6
uv run pytest              # integration tests need postgres and redis running
```

## API contract

`openapi.json` at the repo root is the contract with the front. A test fails when the code and the
file disagree; after an intentional change run `uv run python -m frobi.openapi`, commit the file and
tell the front.

Errors are always `application/problem+json` (RFC 9457) with a stable `code`, for example:

```json
{"type": "about:blank", "title": "Conflict", "status": 409,
 "code": "Tutoring.FinalLocked", "detail": "Se desbloquea después de tu intento.",
 "instance": "/api/v1/help-attempts/…/steps"}
```

## Configuration

Environment variables with the `FROBI_` prefix; see [`.env.example`](./.env.example).
`FROBI_CORS_ORIGINS` takes a comma-separated list.

## Docs

- [`PLAN_BACKEND.md`](./PLAN_BACKEND.md): functional plan, data model and endpoints.
- [`ARCHITECTURE.md`](./ARCHITECTURE.md): module layout and dependency rules.

## License

MIT, see [`LICENSE`](../LICENSE).
