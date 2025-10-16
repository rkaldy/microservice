import contextlib
import logging
from typing import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

from src.db.connection import AsyncConnection

logger = logging.getLogger(__name__)


sa_metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class AsyncEngine:
    def __init__(self, dsn, **kwargs):
        self._engine: AsyncEngine | None = None
        self.dsn = dsn
        self.config = kwargs

    async def __aenter__(self) -> "AsyncEngine":
        self._engine = create_async_engine(self.dsn, **self.config)
        logger.info("Connected to database server.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._engine.dispose()
        logger.info("Disconnected from database server.")

    def connect(self) -> AsyncConnection:
        conn = self._engine.connect()
        return AsyncConnection(conn)

    @contextlib.asynccontextmanager
    async def begin(self) -> AsyncIterator[AsyncConnection]:
        conn = self.connect()
        async with conn:
            async with conn.begin():
                yield conn

    def __getattr__(self, name: str):
        return getattr(self._engine, name)