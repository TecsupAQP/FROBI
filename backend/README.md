# FROBI backend

Backend for FROBI (Hack4Edu 2026): FastAPI + PostgreSQL + Redis, organized as a hexagonal modular monolith.

> Status: phases 0 to 3 done; contract `1.0.0`. Every endpoint of `PLAN_BACKEND.md` §6 exists
> under `/api/v1` with real behaviour. The AI provider is chosen with environment variables
> (Anthropic or any OpenAI-compatible API); without a key, AI features answer from their
> fallbacks (`fallback: true`).
>
> | Module | What works |
> | --- | --- |
> | M1 | Sessions (alias, career, role), `/me`, logout, optional class code |
> | M2 | Onboarding wizard, accessibility profiles and their switches |
> | M3 | Sample guide, paste text, PDF upload, brief + draft (`/works`) |
> | M4/M5 | Formats, adaptations with the 4-piece recipe, 15 s cap, fallback, cache |
> | M6 | Help ladder, «Inténtalo sin IA», hints with fallback |
> | M7 | Prompt scoring (0–4 per piece), improved prompt, autonomy, compare |
> | M8 | Comprehension and transfer questions, answers, «Prueba con…» |
> | M9 | Claim review (supported, unverifiable, contradicts) against own guides |
> | M10 | Fixed catalogue of 5 tools, recommendation by need or reviewed claim |
> | M11 | Personal progress and closing summary |
> | M12 | Classes, invitations, join by code, class content (text or PDF), teacher panel with alerts, student detail |
> | M13 | Settings, alias, leave the class, «Qué ve tu docente», languages |
>
> Privacy (RNF16): every activity row stores the active `class_id`; the teacher panel can only
> read activity of its own class (a test checks before-joining, after-leaving and other-class
> activity never shows up).

## Authentication

1. `POST /api/v1/sessions` with `{"alias": "Ana", "career": "Mecatrónica", "role": "learner"}`.
   The person is stored in Postgres and the token in Redis for 30 days.
   `class_code` is optional: a teacher's class code, or `SENSOR1` for the seeded demo class.
   An unknown code is `422 Classrooms.InvalidCode` and nothing is created.
2. Send the returned token on every other call:
   `Authorization: Bearer <token>`. A missing, made-up or logged-out token is
   `401 Identity.Unauthenticated`.

In `/docs`: call `POST /sessions`, copy the token, then click **Authorize**.

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs Python 3.12 for you)
- Docker Desktop (Postgres 16 and Redis 7)

## Local development

```bash
cp .env.example .env                                        # optional, defaults work locally
uv sync                                                     # dependencies into .venv
docker compose -f docker/compose.yml up -d postgres redis   # databases
uv run alembic upgrade head                                 # create/update tables
uv run uvicorn frobi.main:create_app --factory --reload --reload-dir src  # API on http://localhost:8000
```

- Interactive docs: http://localhost:8000/docs (only while the API is running)
- Health: http://localhost:8000/api/v1/health → `{"status": "ok", "checks": {"postgres": "up", "redis": "up"}}`, or `503` with `"degraded"` if one is down

Everything in Docker, API included: `docker compose -f docker/compose.yml up --build`
(the API container runs the migrations before starting).

New table or column: change the model in `<module>/infrastructure/models.py`, register the
module in `src/frobi/models.py` if it is its first table, then
`uv run alembic revision --autogenerate -m "..."` and review the file. A test fails if models
and migrations disagree.

Integration tests use their own database (`frobi_test`, created and migrated automatically) and
Redis database 15, so they never touch your dev data.

## Checks (same as CI)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run lint-imports        # architecture rules from ARCHITECTURE.md §6
uv run pytest              # integration tests need postgres and redis running
```

## API contract

`openapi.json` at the repo root is the contract with the front, frozen at `1.0.0` for the demo:
from here only additive changes. A test fails when the code and the file disagree; after an intentional change run `uv run python -m frobi.openapi`, commit the file and
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

## AI engine

Set the provider in `.env` (see [`.env.example`](./.env.example)) and restart the API:

```bash
# Anthropic (Claude); the model defaults to claude-haiku-5-5
FROBI_LLM_PROVIDER=anthropic
FROBI_LLM_API_KEY=sk-ant-...

# Or any OpenAI-compatible API (OpenAI, Groq, OpenRouter, Gemini, a local Ollama)
FROBI_LLM_PROVIDER=openai
FROBI_LLM_API_KEY=...
FROBI_LLM_MODEL=llama-3.3-70b-versatile
FROBI_LLM_BASE_URL=https://api.groq.com/openai/v1
```

Without `FROBI_LLM_API_KEY` every AI call answers with its fallback and the response says
`fallback: true`. The same happens per call when the provider fails, takes longer than
`FROBI_LLM_TIMEOUT_SECONDS` (15 s), returns something that does not validate, or the person goes
over `FROBI_LLM_REQUESTS_PER_MINUTE`. For the sample guide the fallback is prewritten
(`modules/adaptations/infrastructure/fallbacks/`); for other materials it reorganizes and
shortens the person's own text without adding anything. The key never leaves the server
(RNF07). Tests never call a provider.

## Demo data

```bash
uv run python -m frobi.demo            # once the migrations are applied
uv run python -m frobi.demo --reset    # start the demo class from scratch
```

The demo class «Sensores 2026-II» (code `SENSOR1`) comes with migration 0010. The script adds
its class content and two students, «Ana (demo)» and «Luis (demo)», whose activity goes through
the real API. It prints a session token for the demo teacher and for each student (use it in
**Authorize** in `/docs`). The panel of the demo class is always `sample_data: true`.

The front does not need those tokens: `POST /sessions/demo` with `{"who": "teacher"}`, `"ana"` or
`"luis"` enters as that person. It only exists with `FROBI_ENVIRONMENT=local` or `demo` (404
anywhere else); the students exist once the script has run. A teacher's classes are listed by
`GET /classes`, so the front never has to remember a class id.

## Docs

- [`PLAN_BACKEND.md`](./PLAN_BACKEND.md): functional plan, data model and endpoints.
- [`ARCHITECTURE.md`](./ARCHITECTURE.md): module layout and dependency rules.

## License

MIT, see [`LICENSE`](../LICENSE).
