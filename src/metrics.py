from prometheus_client import CollectorRegistry, Counter, multiprocess

from src.settings.base import base_settings

registry = CollectorRegistry()
if base_settings.API_SERVER_WORKERS > 1:
    multiprocess.MultiProcessCollector(registry)


retryable_query_error_counter = Counter(
    "retryable_query_errors",
    "Number of retryable database errors that backoff gave up after retries",
    ["error"],
    registry=registry,
)

http_error_counter = Counter(
    "http_errors",
    "Count of error HTTP responses emitted by the API grouped by status code and path.",
    ["status_code", "path"],
    registry=registry,
)
