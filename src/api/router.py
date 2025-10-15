from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.api.response import ORJsonResponse
from src.api.schema import HealthcheckStatus

router = APIRouter(default_response_class=ORJsonResponse)


@router.get(
    "/-/liveness",
    response_model=HealthcheckStatus,
    description="Basic healthcheck endpoint if API application is running.",
    responses={HTTP_200_OK: {"description": "One Offer Rank API is running."}},
    tags=["healthcheck"],
)
async def liveness() -> HealthcheckStatus:
    return HealthcheckStatus(
        status="success", description="One offer rank API is running."
    )