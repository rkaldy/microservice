import contextlib
import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator, Mapping, Optional, Sequence

import backoff
import sqlalchemy.ext.asyncio
from sqlalchemy import CursorResult, Executable
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.exc import DBAPIError

from src.metrics import retryable_query_error_counter
from src.settings.base import DBType
from src.utils.exceptions import RetryableQueryError


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_tries: int
    wait_args: Mapping[str, Any]


class AsyncConnection:
    """Application wrapper around a SQLAlchemy asynchronous connection."""

    type ExecutableParameters = Sequence[Mapping[str, Any]] | Mapping[str, Any] | None

    def __init__(
        self,
        conn: sqlalchemy.ext.asyncio.AsyncConnection,
        retry_policy: RetryPolicy,
    ) -> None:
        self._conn = conn
        self._run_in_transaction_with_backoff = backoff.on_exception(
            wait_gen=backoff.expo,
            exception=RetryableQueryError,
            max_tries=retry_policy.max_tries,
            backoff_log_level=logging.WARNING,
            on_giveup=self._handle_retryable_query_error,
            giveup_log_level=logging.WARNING,
            **retry_policy.wait_args,
        )(self._execute_with_retry)

    async def __aenter__(self) -> "AsyncConnection":
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._conn.__aexit__(exc_type, exc, tb)

    def is_retryable_error(self, err: DBAPIError) -> bool:
        dialect = self._conn.dialect.name
        if dialect == DBType.MYSQL.value:
            error_code = getattr(err.orig, "args", (None,))[0]
            return error_code in {
                1205,  # lock wait timeout
                1213,  # deadlock
            }
        elif dialect == DBType.POSTGRESQL.value:
            error_code = getattr(err.orig, "sqlstate", None)
            return error_code in {
                "40001",  # serialization failure
                "40P01",  # deadlock detected
            }
        return False

    @staticmethod
    def _handle_retryable_query_error(details: Any) -> None:
        exc: RetryableQueryError = details["exception"]
        retryable_query_error_counter.labels(error=exc.__cause__.__class__.__name__).inc()

    async def execute(
        self,
        statement: Executable,
        parameters: ExecutableParameters = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> CursorResult[Any]:
        """Execute a statement without managing its transaction boundary.

        The caller is responsible for committing or rolling back the transaction,
        either explicitly or by using :meth:`transaction`.
        """
        return await self._conn.execute(statement, parameters, execution_options=execution_options)

    async def stream(
        self,
        statement: Executable,
        parameters: ExecutableParameters = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> AsyncIterator[Any]:
        """Stream rows without managing the statement's transaction boundary.

        The caller is responsible for committing or rolling back the transaction,
        either explicitly or by using :meth:`transaction`.
        """
        res = await self._conn.stream(statement, parameters, execution_options=execution_options)
        async for row in res:
            yield row

    @contextlib.asynccontextmanager
    async def transaction(self) -> AsyncIterator["AsyncConnection"]:
        """Open a transaction and expose this connection inside the context.

        A normal exit commits the transaction; an exception rolls it back.
        Nested transactions are not supported.

        Usage:

            async with conn.transaction() as transaction_conn:
                await transaction_conn.execute(...)
        """
        async with self._conn.begin():
            yield self

    async def run_in_transaction(
        self,
        statement: Executable,
        parameters: ExecutableParameters = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> CursorResult[Any]:
        """Execute one statement in a transaction, retrying transient DB errors.

        Every attempt opens a new transaction. A failed attempt is rolled back before
        a retry starts. A successful attempt is committed before the result is returned.
        Non-retryable database errors are raised immediately.

        This method must not be called while the connection already has an active
        transaction. To retry a multi-statement operation atomically, put the retry
        boundary around the complete operation instead.
        """
        return await self._run_in_transaction_with_backoff(
            statement,
            parameters,
            execution_options=execution_options,
        )

    async def _execute_with_retry(
        self,
        statement: Executable,
        parameters: ExecutableParameters = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> CursorResult[Any]:
        try:
            async with self._conn.begin():
                return await self._conn.execute(
                    statement, parameters, execution_options=execution_options
                )
        except DBAPIError as err:
            if self.is_retryable_error(err):
                raise RetryableQueryError(statement) from err.orig
            raise

    async def commit(self) -> None:
        await self._conn.commit()

    async def rollback(self) -> None:
        await self._conn.rollback()

    @property
    def internal(self) -> sqlalchemy.ext.asyncio.AsyncConnection:
        return self._conn
