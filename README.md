# FROBI

FROBI (Hack4Edu 2026): adaptive study materials, help ladder and prompt coaching.

| Folder | What | Docs |
| --- | --- | --- |
| [`backend/`](./backend) | FastAPI + PostgreSQL + Redis API | [`backend/README.md`](./backend/README.md) |
| [`frontend/`](./frontend) | Vue 3 + Vite + Pinia web app (example data behind a service layer) | [`frontend/README.md`](./frontend/README.md) |

The API contract the front consumes is [`backend/openapi.json`](./backend/openapi.json).

## Quickstart (backend)

```bash
cd backend
uv sync
docker compose -f docker/compose.yml up -d postgres redis
uv run uvicorn frobi.main:create_app --factory --reload --reload-dir src
```

Docs at http://localhost:8000/docs while the API is running.

## Quickstart (frontend)

```bash
cd frontend
npm ci
npm run dev
```

Opens at http://localhost:5173. For now it runs on example data; to connect the API, replace each `src/core/<domain>/application/use-case/*.use-case.ts`.

## License

MIT, see [`LICENSE`](./LICENSE).
