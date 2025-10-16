from fastapi import APIRouter, Depends
from sqlalchemy import text
from starlette.status import HTTP_200_OK

from src.api.deps import get_db_conn
from src.api.response import ORJsonResponse
from src.api.schema import HealthcheckStatus
from src.db.connection import AsyncConnection

router = APIRouter(default_response_class=ORJsonResponse)


@router.get(
    "/-/liveness",
    response_model=HealthcheckStatus,
    description="Basic healthcheck endpoint if API application is running.",
    responses={HTTP_200_OK: {"description": "API is running."}},
    tags=["healthcheck"],
)
async def liveness() -> HealthcheckStatus:
    return HealthcheckStatus(status="success", description="API is running.")


@router.get(
    "/-/readiness",
    response_model=HealthcheckStatus,
    description=(
        "Healthcheck endpoint if API application is ready "
        "and all database connections are available."
    ),
    responses={
        HTTP_200_OK: {"description": "API is ready."},
    },
    tags=["healthcheck"],
)
async def readiness(
    db_conn: AsyncConnection = Depends(get_db_conn),
) -> HealthcheckStatus:
    db_version = (await db_conn.execute(text("SELECT VERSION()"))).scalar()
    return HealthcheckStatus(
        status="success",
        description="API is ready.",
        connections={"db_version": db_version},
    )
