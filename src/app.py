import logging

from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.router import router

logger = logging.getLogger(__name__)


def create_api_app():
    app = FastAPI(
        title="Sample",
        description="",
        version="1.0.0",
        docs_url="/-/docs",
        redoc_url="/-/redoc",
        openapi_url="/-/openapi.json",
    )

    app.include_router(router)

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        logger.error("HTTP error: %s", str(exc))
        return await http_exception_handler(request, exc)

    return app
