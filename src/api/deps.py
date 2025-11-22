from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED

from src.db.connection import AsyncConnection
from src.db.engine import AsyncEngine
from src.settings.base import base_settings


async def get_db_engine(request: Request) -> AsyncGenerator[AsyncEngine]:
    yield request.app.state.engine


async def get_db_conn(
    engine: AsyncEngine = Depends(get_db_engine),
) -> AsyncGenerator[AsyncConnection]:
    async with engine.connect() as conn:
        yield conn


def authorize(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    scheme, _, token = authorization.partition(" ")
    if scheme != "Bearer" or token != base_settings.BEARER_TOKEN:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Bearer token")
