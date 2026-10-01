import asyncio
from pathlib import Path
from typing import AsyncGenerator

import pytest
from alembic.config import Config as AlembicConfig

from alembic import command as alembic_command
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
        alembic_config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
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
