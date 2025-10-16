from typing import Optional, Sequence, Mapping, Any, AsyncIterator

import sqlalchemy.ext.asyncio
from sqlalchemy import Executable, CursorResult
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.ext.asyncio import AsyncResult


class AsyncConnection:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def __aenter__(self) -> "AsyncConnection":
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return await self._conn.__aexit__(exc_type, exc, tb)

    async def execute(self,
                      statement: Executable,
                      parameters: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
                      *,
                      execution_options: Optional[CoreExecuteOptionsParameter] = None) -> CursorResult[Any]:
        return await self._conn.execute(statement, parameters, execution_options=execution_options)

    async def stream(self,
        statement: Executable,
        parameters: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
        *,
        execution_options: Optional[CoreExecuteOptionsParameter] = None) -> AsyncIterator[AsyncResult[Any]]:
        async for batch in self._conn.stream(statement, parameters, execution_options=execution_options):
            yield batch

    def __getattr__(self, name: str):
        return getattr(self._conn, name)