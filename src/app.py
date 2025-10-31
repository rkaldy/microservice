import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.router import router
from src.db.engine import AsyncEngine
from src.settings.base import base_settings
from src.utils.log import prepare_logging

prepare_logging()

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

    app.include_router(router)

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        logger.error("HTTP error: %s", str(exc))
        return await http_exception_handler(request, exc)

    return app
