import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import OperationalError

from src.api.deps import get_db_conn


@pytest.mark.anyio
async def test_liveness_does_not_require_database(client: AsyncClient, api_app: FastAPI):
    def unavailable_connection():
        raise AssertionError("Liveness must not access the database")

    api_app.dependency_overrides[get_db_conn] = unavailable_connection

    response = await client.get("/-/liveness")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "description": "API is running.",
        "connections": {},
    }


@pytest.mark.anyio
async def test_readiness_reports_database_version(client: AsyncClient):
    response = await client.get("/-/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["description"] == "API is ready."
    assert isinstance(body["connections"]["db_version"], str)
    assert body["connections"]["db_version"]


@pytest.mark.anyio
async def test_root_is_readiness_alias(client: AsyncClient):
    readiness_response = await client.get("/-/readiness")
    root_response = await client.get("/")

    assert root_response.status_code == 200
    assert root_response.json() == readiness_response.json()


@pytest.mark.anyio
async def test_readiness_fails_when_database_is_unavailable(api_app: FastAPI):
    def unavailable_connection():
        raise OperationalError("SELECT VERSION()", {}, ConnectionError("database unavailable"))

    api_app.dependency_overrides[get_db_conn] = unavailable_connection
    transport = ASGITransport(app=api_app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://api") as client:
        response = await client.get("/-/readiness")

    assert response.status_code == 500
