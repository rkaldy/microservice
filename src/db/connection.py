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
    retryable_query_error_counter.labels(error=exc.__cause__.__class__.__name__)


class AsyncConnection:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def __aenter__(self) -> "AsyncConnection":
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return await self._conn.__aexit__(exc_type, exc, tb)

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=RetryableQueryError,
        max_tries=base_settings.DB_QUERY_RETRY_COUNT,
        backoff_log_level=logging.WARNING,
        on_giveup=handle_retryable_query_error,
        giveup_log_level=logging.WARNING,
        **base_settings.DB_QUERY_RETRY_WAIT_ARGS,
    )
    async def execute(
        self,
        statement: Executable,
        parameters: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> CursorResult[Any]:
        """
        If the query returns an exception that might not occur on retry (for example
        DeadlockDetected), use backoff to retry the query with exponentially increasing
        delay.
        Otherwise raise the exception immediately, because a retry would not help here.
        """
        try:
            return await self._conn.execute(
                statement, parameters, execution_options=execution_options
            )
        except DBAPIError as err:
            err_type = err.orig.__class__.__name__
            if err_type in base_settings.DB_QUERY_RETRYABLE_EXCEPTIONS:
                raise RetryableQueryError(statement) from err.orig
            else:
                raise

    async def stream(
        self,
        statement: Executable,
        parameters: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> AsyncIterator[Any]:
        res = await self._conn.stream(statement, parameters, execution_options=execution_options)
        async for row in res:
            yield row

    def __getattr__(self, name: str):
        return getattr(self._conn, name)
