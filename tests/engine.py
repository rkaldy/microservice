import sqlalchemy as sa

from src.db.engine import AsyncEngine
from src.settings.base import base_settings


class TestAsyncEngine(AsyncEngine):
    """
    DB engine used in unit and integration tests
    """

    async def drop_db_tables(self):
        if base_settings.DB_TYPE == "postgres":
            tables_stmt = sa.text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            async with self.connect() as conn, conn.transaction():
                tables = await conn.execute(tables_stmt)
                for row in tables.fetchall():
                    drop_stmt = sa.text(f"DROP TABLE IF EXISTS {row[0]} CASCADE")
                    await conn.execute(drop_stmt)
        elif base_settings.DB_TYPE == "mysql":
            tables_stmt = sa.text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = :db"
            )
            async with self.connect() as conn, conn.transaction():
                await conn.execute(sa.text("SET FOREIGN_KEY_CHECKS=0"))
                tables = await conn.execute(tables_stmt.bindparams(db=base_settings.DB_NAME))
                for row in tables.fetchall():
                    drop_stmt = sa.text(f"DROP TABLE IF EXISTS {row[0]}")
                    await conn.execute(drop_stmt)
        else:
            raise RuntimeError("Unknown database type", base_settings.DB_TYPE)
