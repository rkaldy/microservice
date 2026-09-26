import pytest
from _pytest.mark import param
from httpx import AsyncClient


@pytest.mark.anyio
async def test_authorized(client: AsyncClient):
    headers = {"Authorization": "Bearer bear"}
    res = await client.get("v1/example", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"status": "success"}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "authorization, error_detail",
    [
        param(None, "Unauthorized", id="missing Bearer token"),
        param("Basic 1234", "Unauthorized", id="invalid authentication scheme"),
        param("Bearer", "Unauthorized", id="missing credentials"),
        param("Bearer wrong", "Invalid Bearer token", id="invalid Bearer token"),
    ],
)
async def test_unauthorized(client: AsyncClient, authorization: str | None, error_detail: str):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization
    res = await client.get("v1/example", headers=headers)
    assert res.status_code == 401
    assert res.json() == {"detail": error_detail}
