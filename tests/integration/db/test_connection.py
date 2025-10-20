import uuid
from typing import AsyncGenerator

import pytest
import sqlalchemy as sa

from src.db.connection import AsyncConnection


@pytest.fixture
async def table(db_conn: AsyncConnection) -> AsyncGenerator[str]:
    table_name = f"test_async_engine_{uuid.uuid4().hex}"
    create_stmt = sa.text(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY)")
    delete_stmt = sa.text(f"DELETE FROM {table_name}")
    insert_stmt = sa.text(f"INSERT INTO {table_name} (id) VALUES (:id)")

    await db_conn.execute(create_stmt)
    for id in [1, 2, 3]:
        await db_conn.execute(insert_stmt, {"id": id})
    yield table_name
    await db_conn.execute(delete_stmt)


@pytest.mark.anyio
async def test_execute(db_conn: AsyncConnection, table: str):
    select_stmt = sa.text(f"SELECT * FROM {table} ORDER BY id")
    result = await db_conn.execute(select_stmt)
    ids = result.scalars().all()
    assert ids == [1, 2, 3]


@pytest.mark.anyio
async def test_stream(db_conn: AsyncConnection, table: str):
    stream_stmt = sa.text(f"SELECT * FROM {table} ORDER BY id DESC")
    ids = [row[0] async for row in db_conn.stream(stream_stmt)]
    assert ids == [3, 2, 1]
