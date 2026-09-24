import uuid
from typing import AsyncGenerator

import pytest
import sqlalchemy as sa
from asyncpg import DeadlockDetectedError, PostgresSyntaxError
from pytest_mock import MockerFixture
from sqlalchemy.exc import DBAPIError

from src.db.connection import AsyncConnection
from src.utils.exceptions import RetryableQueryError


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


@pytest.mark.anyio
async def test_transaction_yields_wrapped_connection(mocker: MockerFixture):
    conn_mock = mocker.Mock()
    transaction_mock = mocker.MagicMock()
    transaction_mock.__aenter__ = mocker.AsyncMock()
    transaction_mock.__aexit__ = mocker.AsyncMock(return_value=False)
    conn_mock.begin.return_value = transaction_mock
    conn = AsyncConnection(conn_mock)

    async with conn.transaction() as transaction_conn:
        assert transaction_conn is conn

    conn_mock.begin.assert_called_once_with()
    transaction_mock.__aexit__.assert_awaited_once_with(None, None, None)


@pytest.mark.anyio
async def test_run_in_transaction(mocker: MockerFixture):
    expected_result = mocker.sentinel.result
    conn_mock = mocker.Mock()
    conn_mock.execute = mocker.AsyncMock(return_value=expected_result)
    transaction_mock = mocker.MagicMock()
    transaction_mock.__aenter__ = mocker.AsyncMock()
    transaction_mock.__aexit__ = mocker.AsyncMock(return_value=False)
    conn_mock.begin.return_value = transaction_mock
    conn = AsyncConnection(conn_mock)

    result = await conn.run_in_transaction(sa.text("SELECT 1"))

    assert result is expected_result
    conn_mock.begin.assert_called_once_with()
    transaction_mock.__aexit__.assert_awaited_once_with(None, None, None)


@pytest.mark.anyio
async def test_retryable_query_error_starts_new_transaction_for_each_attempt(
    mocker: MockerFixture, caplog
):
    conn_mock = mocker.Mock()
    conn_mock.execute = mocker.AsyncMock(side_effect=DBAPIError("", {}, DeadlockDetectedError("")))
    transaction_mock = mocker.MagicMock()
    transaction_mock.__aenter__ = mocker.AsyncMock()
    transaction_mock.__aexit__ = mocker.AsyncMock(return_value=False)
    conn_mock.begin.return_value = transaction_mock
    conn = AsyncConnection(conn_mock)

    with pytest.raises(RetryableQueryError) as ex:
        await conn.run_in_transaction(sa.text(""))

    assert isinstance(ex.value.__cause__, DeadlockDetectedError)
    assert conn_mock.begin.call_count == 3
    assert transaction_mock.__aexit__.await_count == 3
    assert all(call.args[0] is DBAPIError for call in transaction_mock.__aexit__.await_args_list)
    assert "Backing off run_in_transaction(...)" in caplog.messages[-3]
    assert "Backing off run_in_transaction(...)" in caplog.messages[-2]
    assert "Giving up run_in_transaction(...)" in caplog.messages[-1]


@pytest.mark.anyio
async def test_non_retryable_query_error(mocker: MockerFixture, caplog):
    conn_mock = mocker.Mock()
    conn_mock.execute = mocker.AsyncMock(side_effect=DBAPIError("", {}, PostgresSyntaxError("")))
    transaction_mock = mocker.MagicMock()
    transaction_mock.__aenter__ = mocker.AsyncMock()
    transaction_mock.__aexit__ = mocker.AsyncMock(return_value=False)
    conn_mock.begin.return_value = transaction_mock
    conn = AsyncConnection(conn_mock)

    with pytest.raises(DBAPIError) as ex:
        await conn.run_in_transaction(sa.text(""))

    assert isinstance(ex.value.orig, PostgresSyntaxError)
    conn_mock.begin.assert_called_once_with()
    assert transaction_mock.__aexit__.await_args.args[0] is DBAPIError
    assert not caplog.messages
