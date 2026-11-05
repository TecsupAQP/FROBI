# FROBI

FROBI (Hack4Edu 2026): adaptive study materials, help ladder and prompt coaching.

| Folder | What | Docs |
| --- | --- | --- |
| [`backend/`](./backend) | FastAPI + PostgreSQL + Redis API | [`backend/README.md`](./backend/README.md) |
| [`frontend/`](./frontend) | Vue 3 + Vite + Pinia web app, connected to the API | [`frontend/README.md`](./frontend/README.md) |
| [`deploy/`](./deploy) | Docker Compose + Caddy for a VPS | [`deploy/README.md`](./deploy/README.md) |

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

Opens at http://localhost:5173 and talks to the API at http://localhost:8000/api/v1 (start the backend first; change it with `VITE_API_URL`).

## Deploy on a VPS

Front, API, Postgres and Redis behind Caddy (automatic HTTPS) with one command:
see [`deploy/README.md`](./deploy/README.md).

## License

MIT, see [`LICENSE`](./LICENSE).
