import sqlalchemy as sa

from src.db.engine import AsyncEngine
from src.settings.base import DBType


class TestAsyncEngine(AsyncEngine):
    """
    DB engine used in unit and integration tests
    """

    async def __aenter__(self) -> "TestAsyncEngine":
        await super().__aenter__()
        return self

    async def drop_db_tables(self):
        dialect = self._engine.dialect.name
        if dialect == DBType.POSTGRESQL.value:
            tables_stmt = sa.text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            async with self.connect() as conn, conn.transaction():
                tables = await conn.execute(tables_stmt)
                for row in tables.fetchall():
                    drop_stmt = sa.text(f"DROP TABLE IF EXISTS {row[0]} CASCADE")
                    await conn.execute(drop_stmt)
        elif dialect == DBType.MYSQL.value:
            tables_stmt = sa.text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = :db"
            )
            async with self.connect() as conn, conn.transaction():
                await conn.execute(sa.text("SET FOREIGN_KEY_CHECKS=0"))
                tables = await conn.execute(tables_stmt.bindparams(db=self._engine.url.database))
                for row in tables.fetchall():
                    drop_stmt = sa.text(f"DROP TABLE IF EXISTS {row[0]}")
                    await conn.execute(drop_stmt)
        else:
            raise RuntimeError(f"Unknown database type {dialect}")
