from typing import AsyncGenerator

import pytest
from fastapi import FastAPI

from src.api.deps import get_db_conn
from src.app import create_api_app
from src.db.connection import AsyncConnection
from src.settings.base import Settings


@pytest.fixture
async def api_app(db_conn: AsyncConnection, settings: Settings) -> AsyncGenerator[FastAPI]:
    app = create_api_app(settings)
    app.dependency_overrides[get_db_conn] = lambda: db_conn
    yield app
