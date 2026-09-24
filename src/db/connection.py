import contextlib
import logging
from typing import Any, AsyncIterator, Mapping, Optional, Sequence

import backoff
import sqlalchemy.ext.asyncio
from sqlalchemy import CursorResult, Executable
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.exc import DBAPIError

from src.metrics import retryable_query_error_counter
from src.settings.base import base_settings
from src.utils.exceptions import RetryableQueryError


def handle_retryable_query_error(details):
    exc: RetryableQueryError = details["exception"]
    retryable_query_error_counter.labels(error=exc.__cause__.__class__.__name__).inc()


class AsyncConnection:
    """Application wrapper around a SQLAlchemy asynchronous connection."""

    type ExecutableParameters = Sequence[Mapping[str, Any]] | Mapping[str, Any] | None

    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def __aenter__(self) -> "AsyncConnection":
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._conn.__aexit__(exc_type, exc, tb)

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

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=RetryableQueryError,
        max_tries=base_settings.DB_QUERY_RETRY_COUNT,
        backoff_log_level=logging.WARNING,
        on_giveup=handle_retryable_query_error,
        giveup_log_level=logging.WARNING,
        **base_settings.DB_QUERY_RETRY_WAIT_ARGS,
    )
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
        try:
            async with self._conn.begin():
                return await self._conn.execute(
                    statement, parameters, execution_options=execution_options
                )
        except DBAPIError as err:
            err_type = err.orig.__class__.__name__
            if err_type in base_settings.DB_QUERY_RETRYABLE_EXCEPTIONS:
                raise RetryableQueryError(statement) from err.orig
            raise

    def __getattr__(self, name: str):
        return getattr(self._conn, name)
