import pytest
from httpx import AsyncClient
from prometheus_client import generate_latest

from src.metrics import http_error_counter, registry


@pytest.mark.anyio
async def test_http_error_metrics(client: AsyncClient):
    not_found_metric = http_error_counter.labels(status_code="404", path="/invalid")
    method_not_allowed_metric = http_error_counter.labels(status_code="405", path="/-/liveness")
    not_found_metric._value.set(0)
    method_not_allowed_metric._value.set(0)

    for _ in range(3):
        await client.get("/invalid")  # HTTP/404 Not found
    for _ in range(2):
        await client.head("/-/liveness")  # HTTP/405 Method Not Allowed

    assert not_found_metric._value.get() == 3
    assert method_not_allowed_metric._value.get() == 2

    metrics_output = generate_latest(registry).decode()
    assert 'http_errors_total{path="/invalid",status_code="404"} 3.0' in metrics_output
    assert 'http_errors_total{path="/-/liveness",status_code="405"} 2.0' in metrics_output
