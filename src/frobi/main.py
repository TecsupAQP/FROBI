"""Application factory. Module routers are mounted here as they are implemented."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from frobi.shared.infrastructure import (
    PostgresProbe,
    RedisProbe,
    Settings,
    create_engine,
    create_redis,
    create_session_factory,
    get_settings,
)
from frobi.shared.presentation import PROBLEM_RESPONSES, health_router, register_problem_handlers

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    # Neither the engine nor the Redis client connects until first use, so building the app
    # (tests, OpenAPI export) works without Postgres or Redis running.
    engine = create_engine(settings.database_url)
    redis = create_redis(settings.redis_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await redis.aclose()
        await engine.dispose()

    app = FastAPI(
        title="FROBI API",
        version="0.1.0",
        description="Backend de FROBI (Hack4Edu 2026). Los errores siguen RFC 9457 "
        "(`application/problem+json`) con un `code` estable.",
        lifespan=lifespan,
        responses=PROBLEM_RESPONSES,
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = redis
    app.state.health_probes = [PostgresProbe(engine), RedisProbe(redis)]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_problem_handlers(app)
    app.include_router(health_router, prefix=API_PREFIX)
    return app
