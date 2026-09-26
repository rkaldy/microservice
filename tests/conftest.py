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
from src.db.engine import AsyncEngine
from src.settings.base import Settings
from tests.engine import TestAsyncEngine


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
async def db_engine(settings: Settings) -> AsyncGenerator[AsyncEngine]:
    async with TestAsyncEngine(settings) as engine:
        await engine.drop_db_tables()
        alembic_config_path = Path(__name__).absolute().parent / "alembic.ini"
        alembic_config = AlembicConfig(str(alembic_config_path))
        alembic_config.attributes["settings"] = settings
        upgrade_coro = asyncio.to_thread(alembic_command.upgrade, alembic_config, "head")
        await upgrade_coro
        yield engine
        await engine.drop_db_tables()


@pytest.fixture
async def db_conn(db_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection]:
    async with db_engine.connect() as conn, conn.transaction() as conn:
        yield conn
        await conn.rollback()


@pytest.fixture
async def api_app(db_conn: AsyncConnection, settings: Settings) -> AsyncGenerator[FastAPI]:
    """
    Creates a FastAPI app instance, using database connections from TestAsyncEngine
    """
    app = create_api_app(settings)
    app.dependency_overrides[get_db_conn] = lambda: db_conn
    yield app
