import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.probe import router as probe_router
from src.api.v1.router import router as api_router
from src.db.engine import AsyncEngine
from src.settings.base import base_settings
from src.utils.log import prepare_logging
from src.utils.sentry import init_sentry

prepare_logging()
init_sentry(server_name="api-server", component="api")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = AsyncEngine(
        base_settings,
        pool_size=base_settings.DB_POOL_SIZE,
        max_overflow=0,
        pool_timeout=base_settings.DB_POOL_TIMEOUT,
        pool_recycle=base_settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )
    async with app.state.engine:
        yield


def create_api_app():
    app = FastAPI(
        title="Sample",
        description="",
        version="1.0.0",
        docs_url="/-/docs",
        redoc_url="/-/redoc",
        openapi_url="/-/openapi.json",
        lifespan=lifespan,
    )

    app.include_router(probe_router)
    app.include_router(api_router)
    return app
