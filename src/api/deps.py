from typing import AsyncGenerator

from fastapi import Depends, Request

from src.db.connection import AsyncConnection
from src.db.engine import AsyncEngine


async def get_db_engine(request: Request) -> AsyncGenerator[AsyncEngine]:
    yield request.app.state.engine


async def get_db_conn(
    engine: AsyncEngine = Depends(get_db_engine),
) -> AsyncGenerator[AsyncConnection]:
    async with engine.connect() as conn:
        yield conn
