import contextlib
import logging
import ssl
from typing import AsyncIterator

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

from src.db.connection import AsyncConnection
from src.settings.base import Settings

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
    def __init__(self, settings: Settings, **kwargs) -> None:
        self._engine: sqlalchemy.ext.asyncio.engine.AsyncEngine | None = None
        self.dsn = settings.db_dsn
        self.config = kwargs
        if settings.DB_SSL_ENABLED:
            ssl_ctx = ssl.create_default_context(cafile=settings.DB_SSL_CA_PATH)
            if settings.DB_SSL_VERIFY_CERT:
                ssl_ctx.check_hostname = True
                ssl_ctx.verify_mode = ssl.CERT_REQUIRED
            else:
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE
            self.config["connect_args"] = {"ssl": ssl_ctx}

    async def __aenter__(self) -> "AsyncEngine":
        self._engine = create_async_engine(self.dsn, **self.config)
        logger.info("Connected to database server.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._engine:
            await self._engine.dispose()
        logger.info("Disconnected from database server.")

    def connect(self) -> AsyncConnection:
        if not self._engine:
            raise RuntimeError("AsyncEngine not initialized")
        conn = self._engine.connect()
        return AsyncConnection(conn)

    @contextlib.asynccontextmanager
    async def begin(self) -> AsyncIterator[AsyncConnection]:
        conn = self.connect()
        async with conn, conn.begin():
            yield conn

    def __getattr__(self, name: str):
        return getattr(self._engine, name)
