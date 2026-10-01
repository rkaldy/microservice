from unittest.mock import MagicMock, Mock

import pytest
import sqlalchemy as sa
from asyncpg import DeadlockDetectedError, PostgresSyntaxError
from pytest_mock import MockerFixture
from sqlalchemy.exc import DBAPIError

from src.db.connection import AsyncConnection, RetryPolicy
from src.metrics import retryable_query_error_counter
from src.utils.exceptions import RetryableQueryError


@pytest.fixture
def retry_policy() -> RetryPolicy:
    return RetryPolicy(max_tries=3, wait_args={"factor": 0.0})


@pytest.fixture
def transaction_mock(mocker: MockerFixture) -> MagicMock:
    transaction = mocker.MagicMock()
    transaction.__aenter__ = mocker.AsyncMock()
    transaction.__aexit__ = mocker.AsyncMock(return_value=False)
    return transaction


@pytest.fixture
def internal_connection(mocker: MockerFixture, transaction_mock: MagicMock) -> Mock:
    connection = mocker.Mock()
    connection.dialect.name = "postgresql"
    connection.begin.return_value = transaction_mock
    return connection


@pytest.mark.anyio
async def test_run_in_transaction(
    mocker: MockerFixture,
    internal_connection: Mock,
    transaction_mock: MagicMock,
    retry_policy: RetryPolicy,
):
    expected_result = mocker.sentinel.result
    internal_connection.execute = mocker.AsyncMock(return_value=expected_result)
    connection = AsyncConnection(internal_connection, retry_policy)

    result = await connection.run_in_transaction(sa.text("SELECT 1"))

    assert result is expected_result
    internal_connection.begin.assert_called_once_with()
    transaction_mock.__aexit__.assert_awaited_once_with(None, None, None)


@pytest.mark.anyio
async def test_retryable_query_error_starts_new_transaction_for_each_attempt(
    mocker: MockerFixture,
    caplog,
    internal_connection: Mock,
    transaction_mock: MagicMock,
    retry_policy: RetryPolicy,
):
    internal_connection.execute = mocker.AsyncMock(
        side_effect=DBAPIError("", {}, DeadlockDetectedError(""))
    )
    connection = AsyncConnection(internal_connection, retry_policy)

    with pytest.raises(RetryableQueryError) as ex:
        await connection.run_in_transaction(sa.text(""))

    assert isinstance(ex.value.__cause__, DeadlockDetectedError)
    assert internal_connection.begin.call_count == 3
    assert transaction_mock.__aexit__.await_count == 3
    assert all(call.args[0] is DBAPIError for call in transaction_mock.__aexit__.await_args_list)
    assert "Backing off _execute_with_retry(...)" in caplog.messages[-3]
    assert "Backing off _execute_with_retry(...)" in caplog.messages[-2]
    assert "Giving up _execute_with_retry(...)" in caplog.messages[-1]


@pytest.mark.anyio
async def test_non_retryable_query_error(
    mocker: MockerFixture,
    caplog,
    internal_connection: Mock,
    transaction_mock: MagicMock,
    retry_policy: RetryPolicy,
):
    internal_connection.execute = mocker.AsyncMock(
        side_effect=DBAPIError("", {}, PostgresSyntaxError(""))
    )
    connection = AsyncConnection(internal_connection, retry_policy)

    with pytest.raises(DBAPIError) as ex:
        await connection.run_in_transaction(sa.text(""))

    assert isinstance(ex.value.orig, PostgresSyntaxError)
    internal_connection.begin.assert_called_once_with()
    assert transaction_mock.__aexit__.await_args.args[0] is DBAPIError
    assert not caplog.messages


class DatabaseError(Exception):
    sqlstate: str | None = None


def dbapi_error(*, args: tuple[object, ...] = (), sqlstate: str | None = None) -> DBAPIError:
    original = DatabaseError(*args)
    original.sqlstate = sqlstate
    return DBAPIError("", {}, original)


@pytest.mark.parametrize(
    ("dialect", "error", "expected"),
    [
        pytest.param(
            "postgresql", dbapi_error(sqlstate="40001"), True, id="postgres-serialization"
        ),
        pytest.param(
            "postgresql+asyncpg", dbapi_error(sqlstate="40P01"), True, id="postgres-deadlock"
        ),
        pytest.param("postgresql", dbapi_error(sqlstate="42601"), False, id="postgres-other"),
        pytest.param("mysql", dbapi_error(args=(1205, "timeout")), True, id="mysql-timeout"),
        pytest.param(
            "mysql+aiomysql", dbapi_error(args=(1213, "deadlock")), True, id="mysql-deadlock"
        ),
        pytest.param("mysql", dbapi_error(args=(1064, "syntax")), False, id="mysql-other"),
        pytest.param("sqlite", dbapi_error(), False, id="unsupported-dialect"),
    ],
)
def test_is_retryable_error(
    internal_connection: Mock,
    retry_policy: RetryPolicy,
    dialect: str,
    error: DBAPIError,
    expected: bool,
):
    internal_connection.dialect.name = dialect
    connection = AsyncConnection(internal_connection, retry_policy)

    assert connection.is_retryable_error(error) is expected


@pytest.mark.anyio
async def test_retryable_error_increments_giveup_metric_once(
    mocker: MockerFixture,
    internal_connection: Mock,
    transaction_mock: MagicMock,
    retry_policy: RetryPolicy,
):
    metric = retryable_query_error_counter.labels(error="DeadlockDetectedError")
    metric._value.set(0)
    internal_connection.execute = mocker.AsyncMock(
        side_effect=DBAPIError("", {}, DeadlockDetectedError(""))
    )
    connection = AsyncConnection(internal_connection, retry_policy)

    try:
        with pytest.raises(RetryableQueryError):
            await connection.run_in_transaction(sa.text("SELECT 1"))

        assert internal_connection.execute.await_count == retry_policy.max_tries
        assert internal_connection.begin.call_count == retry_policy.max_tries
        assert transaction_mock.__aexit__.await_count == retry_policy.max_tries
        assert metric._value.get() == 1
    finally:
        metric._value.set(0)


@pytest.mark.anyio
async def test_successful_retry_does_not_increment_giveup_metric(
    mocker: MockerFixture,
    internal_connection: Mock,
    transaction_mock: MagicMock,
    retry_policy: RetryPolicy,
):
    metric = retryable_query_error_counter.labels(error="DeadlockDetectedError")
    metric._value.set(0)
    expected_result = mocker.sentinel.result
    internal_connection.execute = mocker.AsyncMock(
        side_effect=[DBAPIError("", {}, DeadlockDetectedError("")), expected_result]
    )
    connection = AsyncConnection(internal_connection, retry_policy)

    try:
        result = await connection.run_in_transaction(sa.text("SELECT 1"))

        assert result is expected_result
        assert internal_connection.begin.call_count == 2
        assert transaction_mock.__aexit__.await_count == 2
        assert metric._value.get() == 0
    finally:
        metric._value.set(0)
