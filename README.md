# FROBI backend

Backend for FROBI (Hack4Edu 2026): FastAPI + PostgreSQL + Redis, organized as a hexagonal modular monolith.

> Status: repository structure only. No endpoints or use cases are implemented yet.

## Quickstart

```bash
docker compose -f docker/compose.yml up
```

## Local development

```bash
uv sync
uv run uvicorn frobi.main:create_app --factory --reload
uv run ruff check .
uv run pytest
```

Configuration uses environment variables with the `FROBI_` prefix (`FROBI_DATABASE_URL`, `FROBI_REDIS_URL`, `FROBI_CORS_ORIGINS`, `FROBI_LLM_API_KEY`, `FROBI_LLM_TIMEOUT_SECONDS`).

## Docs

- [`PLAN_BACKEND.md`](./PLAN_BACKEND.md): functional plan, data model and endpoints.
- [`ARCHITECTURE.md`](./ARCHITECTURE.md): module layout and dependency rules.

## License

MIT, see [`LICENSE`](./LICENSE).
