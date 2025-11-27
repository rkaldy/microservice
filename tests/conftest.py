import asyncio
from pathlib import Path
from typing import AsyncGenerator

import pytest
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI

from alembic import command as alembic_command
from src.api.deps import get_db_conn
from src.app import create_api_app
from src.db.connection import AsyncConnection
from src.settings.base import base_settings
from tests.engine import TestAsyncEngine


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[TestAsyncEngine]:
    async with TestAsyncEngine(base_settings) as engine:
        alembic_config_path = Path(__name__).absolute().parent / "alembic.ini"
        upgrade_coro = asyncio.to_thread(
            alembic_command.upgrade, AlembicConfig(str(alembic_config_path)), "head"
        )
        await upgrade_coro
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
