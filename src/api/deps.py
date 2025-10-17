import logging
from typing import AsyncGenerator

from src.db.connection import AsyncConnection
from src.db.engine import AsyncEngine
from src.settings.base import base_settings

logger = logging.getLogger(__name__)


async def get_db_conn() -> AsyncGenerator[AsyncConnection]:
    async with AsyncEngine(base_settings.db_dsn) as engine, engine.connect() as conn:
        yield conn
