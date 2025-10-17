import contextlib
from typing import AsyncIterator

import sqlalchemy as sa

from src.db.connection import AsyncConnection
from src.db.engine import AsyncEngine


class TestAsyncEngine(AsyncEngine):
    """
    DB engine used in unit and integration tests
    At the start and end of testsuite, drops all tables, so the testsuite can create the database schema from scratch
    using alembic migration scripts.
    At the end of each tests, rollback the transaction, so every test begins with clean empty database.
    """

    async def __aenter__(self) -> "TestAsyncEngine":
        await self.drop_db_tables()
        await super().__aenter__()
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
        async with self.begin() as conn:
            select_all_tables_stmt = (
                sa.select(sa.column("tablename").label("name"))
                .select_from(sa.text("pg_tables"))
                .where(sa.literal_column("schemaname") == "public")
            )
            for table in await conn.execute(select_all_tables_stmt):
                stmt = sa.text(f"DROP TABLE IF EXISTS {table.name} CASCADE")
                await conn.execute(stmt)
