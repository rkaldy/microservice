import contextlib
from typing import AsyncIterator

import sqlalchemy as sa

from src.db.connection import AsyncConnection
from src.db.engine import AsyncEngine
from src.settings.base import base_settings


class TestAsyncEngine(AsyncEngine):
    """
    DB engine used in unit and integration tests
    At the start and end of testsuite, drops all tables, so the testsuite can create the database schema from scratch
    using alembic migration scripts.
    At the end of each tests, rollback the transaction, so every test begins with clean empty database.
    """

    async def __aenter__(self) -> "TestAsyncEngine":
        await super().__aenter__()
        await self.drop_db_tables()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.drop_db_tables()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    @contextlib.asynccontextmanager
    async def begin(self) -> AsyncIterator[AsyncConnection]:
        async with super().begin() as conn:
            yield conn
            await conn.rollback()

    async def drop_db_tables(self):
        if "postgres" in base_settings.DB_PROTOCOL:
            tables_stmt = sa.text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            async with self.begin() as conn:
                tables = await conn.execute(tables_stmt)
                for row in tables.fetchall():
                    drop_stmt = sa.text(f"DROP TABLE IF EXISTS {row[0]} CASCADE")
                    await conn.execute(drop_stmt)
        elif "mysql" in base_settings.DB_PROTOCOL:
            tables_stmt = sa.text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = :db"
            )
            async with super().begin() as conn:
                await conn.execute(sa.text("SET FOREIGN_KEY_CHECKS=0"))
                tables = await conn.execute(tables_stmt.bindparams(db=base_settings.DB_NAME))
                for row in tables.fetchall():
                    drop_stmt = sa.text(f"DROP TABLE IF EXISTS {row[0]}")
                    await conn.execute(drop_stmt)
        else:
            raise RuntimeError("Unknown database protocol", base_settings.DB_PROTOCOL)
