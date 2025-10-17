import logging
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI

from src.api.deps import get_db_conn
from src.app import create_api_app
from src.db.connection import AsyncConnection
from src.settings.base import base_settings
from tests.engine import TestAsyncEngine


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def enable_all_loggers():
    for name in logging.root.manager.loggerDict:
        if name.startswith("src"):
            logger = logging.getLogger(name)
            logger.disabled = False


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[TestAsyncEngine]:
    async with TestAsyncEngine(base_settings.db_dsn) as engine:
        yield engine


@pytest.fixture
async def db_conn(db_engine: TestAsyncEngine) -> AsyncGenerator[AsyncConnection]:
    async with db_engine.begin() as conn:
        yield conn


@pytest.fixture
async def api_app(db_conn: AsyncConnection) -> AsyncGenerator[FastAPI]:
    """
    Creates a FastAPI app instance, using database connections from TestAsyncEngine
    """
    app = create_api_app()
    app.dependency_overrides[get_db_conn] = lambda: db_conn
    yield app
