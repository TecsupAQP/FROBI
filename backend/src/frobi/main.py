"""Application factory. Module routers are mounted here as they are implemented."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from frobi.modules.adaptations.presentation.router import router as adaptations_router
from frobi.modules.claim_review.presentation.router import router as claim_review_router
from frobi.modules.classrooms.infrastructure import ClassroomsClassContext
from frobi.modules.classrooms.presentation.router import router as classrooms_router
from frobi.modules.comprehension.presentation.router import router as comprehension_router
from frobi.modules.identity.infrastructure import RedisSessionStore
from frobi.modules.identity.presentation.router import router as identity_router
from frobi.modules.materials.presentation.router import router as materials_router
from frobi.modules.onboarding.presentation.router import me_router as onboarding_me_router
from frobi.modules.onboarding.presentation.router import router as onboarding_router
from frobi.modules.progress.presentation.router import router as progress_router
from frobi.modules.prompt_coach.presentation.router import router as prompt_coach_router
from frobi.modules.settings.presentation.router import router as settings_router
from frobi.modules.tools.presentation.router import router as tools_router
from frobi.modules.tutoring.presentation.router import router as tutoring_router
from frobi.shared.infrastructure import (
    PostgresProbe,
    RedisProbe,
    Settings,
    SystemClock,
    create_engine,
    create_redis,
    create_session_factory,
    get_settings,
)
from frobi.shared.infrastructure.llm import build_llm_client
from frobi.shared.presentation import PROBLEM_RESPONSES, health_router, register_problem_handlers

API_PREFIX = "/api/v1"

# Sections of /docs, in the order of the demo flow. Names must match each router's tag.
SECTION_ORDER = [
    "health",
    "M1 · Cuenta y acceso",
    "M2 · Primera configuración",
    "M3 · Material",
    "M4 y M5 · Adaptación",
    "M6 · Escalera de ayuda",
    "M7 · Entrenador de instrucciones",
    "M8 · Verificación",
    "M9 · Revisión de afirmaciones",
    "M10 · Herramientas",
    "M11 · Progreso y cierre",
    "M12 · Clase del docente",
    "M13 · Ajustes y privacidad",
]

MODULE_ROUTERS = [
    identity_router,
    onboarding_router,
    onboarding_me_router,
    materials_router,
    adaptations_router,
    tutoring_router,
    prompt_coach_router,
    comprehension_router,
    claim_review_router,
    tools_router,
    progress_router,
    classrooms_router,
    settings_router,
]


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
        version="1.0.0",
        description="Backend de FROBI (Hack4Edu 2026). Los errores siguen RFC 9457 "
        "(`application/problem+json`) con un `code` estable.",
        lifespan=lifespan,
        responses=PROBLEM_RESPONSES,
        openapi_tags=[{"name": name} for name in SECTION_ORDER],
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = redis
    app.state.health_probes = [PostgresProbe(engine), RedisProbe(redis)]
    app.state.clock = SystemClock()
    # Every router authenticates through this resolver (see shared.presentation.auth).
    app.state.token_resolver = RedisSessionStore(redis)
    # class_id stored on every activity row (RNF16): the person's joined class.
    app.state.class_context = ClassroomsClassContext(app.state.session_factory)
    # Without FROBI_LLM_API_KEY every AI call uses its fallback and answers `fallback: true`.
    app.state.llm = build_llm_client(
        provider=settings.llm_provider,
        api_key=None if settings.llm_api_key is None else settings.llm_api_key.get_secret_value(),
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        timeout_seconds=settings.llm_timeout_seconds,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_problem_handlers(app)

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse("/docs")

    app.include_router(health_router, prefix=API_PREFIX)
    for router in MODULE_ROUTERS:
        app.include_router(router, prefix=API_PREFIX)
    return app
