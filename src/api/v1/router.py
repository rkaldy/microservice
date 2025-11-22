from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from src.api.deps import authorize
from src.api.response import ORJsonResponse
from src.api.v1.schemas import ExampleResponse

router = APIRouter(prefix="/v1", default_response_class=ORJsonResponse)


@router.get(
    "/example",
    response_model=ExampleResponse,
    description="An example endpoint",
    responses={HTTP_200_OK: {"status": "success"}},
    dependencies=[Depends(authorize)],
)
async def example() -> ExampleResponse:
    return ExampleResponse(status="success")
