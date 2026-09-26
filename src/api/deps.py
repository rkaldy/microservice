from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from src.db.connection import AsyncConnection
from src.db.engine import AsyncEngine

http_bearer = HTTPBearer(auto_error=False)


async def get_db_engine(request: Request) -> AsyncGenerator[AsyncEngine]:
    yield request.app.state.engine


async def get_db_conn(
    engine: AsyncEngine = Depends(get_db_engine),
) -> AsyncGenerator[AsyncConnection]:
    async with engine.connect() as conn:
        yield conn


def authorize(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> None:
    if credentials is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
        )
    if credentials.credentials != request.app.state.settings.BEARER_TOKEN:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid Bearer token")
