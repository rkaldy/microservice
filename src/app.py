from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.health import router as probe_router
from src.api.metrics import router as metrics_router
from src.api.v1.router import router as api_router
from src.db.engine import AsyncEngine
from src.prometheus_middleware import PrometheusMetricsMiddleware
from src.settings.base import Settings
from src.utils.log import prepare_logging
from src.utils.sentry import init_sentry


def create_api_app(settings: Settings | None = None):
    settings = settings or Settings()

    prepare_logging(settings)
    init_sentry(settings, server_name="api-server", component="api")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.engine = AsyncEngine(
            settings,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=0,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
        )
        async with app.state.engine:
            yield

    app = FastAPI(
        title="Sample",
        description="",
        version="1.0.0",
        docs_url="/-/docs",
        redoc_url="/-/redoc",
        openapi_url="/-/openapi.json",
        lifespan=lifespan,
    )

    app.state.settings = settings
    app.add_middleware(PrometheusMetricsMiddleware)
    app.include_router(probe_router)
    app.include_router(metrics_router)
    app.include_router(api_router)
    return app
