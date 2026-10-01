import pytest
from fastapi import FastAPI, Response
from httpx import AsyncClient
from prometheus_client import generate_latest

from src.metrics import http_error_counter, registry, retryable_query_error_counter


@pytest.mark.anyio
async def test_metrics_endpoint(client: AsyncClient):
    retry_metric = retryable_query_error_counter.labels(error="IntegrationTestError")
    retry_metric._value.set(0)
    try:
        retry_metric.inc()

        response = await client.get("/-/metrics")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
        assert "# HELP http_errors_total" in response.text
        assert "# TYPE http_errors_total counter" in response.text
        assert 'retryable_query_errors_total{error="IntegrationTestError"} 1.0' in response.text
    finally:
        retry_metric._value.set(0)


@pytest.mark.anyio
async def test_http_error_metrics(client: AsyncClient, api_app: FastAPI):
    route_template = "/test-errors/{resource_id}"
    exception_route_template = "/test-exceptions/{resource_id}"
    not_found_metric = http_error_counter.labels(status_code="404", path="unmatched")
    method_not_allowed_metric = http_error_counter.labels(status_code="405", path="/-/liveness")
    dynamic_route_metric = http_error_counter.labels(status_code="400", path=route_template)
    exception_route_metric = http_error_counter.labels(
        status_code="500", path=exception_route_template
    )
    not_found_metric._value.set(0)
    method_not_allowed_metric._value.set(0)
    dynamic_route_metric._value.set(0)
    exception_route_metric._value.set(0)

    @api_app.get(route_template)
    async def test_error_route(resource_id: str):
        return Response(status_code=400)

    @api_app.get(exception_route_template)
    async def test_exception_route(resource_id: str):
        raise RuntimeError("Test error")

    for _ in range(3):
        await client.get("/invalid")  # HTTP/404 Not found
    for _ in range(2):
        await client.head("/-/liveness")  # HTTP/405 Method Not Allowed
    await client.get("/test-errors/first")
    await client.get("/test-errors/second")
    with pytest.raises(RuntimeError, match="Test error"):
        await client.get("/test-exceptions/first")

    assert not_found_metric._value.get() == 3
    assert method_not_allowed_metric._value.get() == 2
    assert dynamic_route_metric._value.get() == 2
    assert exception_route_metric._value.get() == 1

    metrics_output = generate_latest(registry).decode()
    assert 'http_errors_total{path="unmatched",status_code="404"} 3.0' in metrics_output
    assert 'http_errors_total{path="/-/liveness",status_code="405"} 2.0' in metrics_output
    assert (
        'http_errors_total{path="/test-errors/{resource_id}",status_code="400"} 2.0'
        in metrics_output
    )
    assert (
        'http_errors_total{path="/test-exceptions/{resource_id}",status_code="500"} 1.0'
        in metrics_output
    )
    assert 'path="/test-errors/first"' not in metrics_output
    assert 'path="/test-errors/second"' not in metrics_output
