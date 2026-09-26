from prometheus_client import CollectorRegistry, Counter

registry = CollectorRegistry()


retryable_query_error_counter = Counter(
    "retryable_query_errors",
    "Number of retryable database errors that backoff gave up after retries",
    ["error"],
    registry=registry,
)

http_error_counter = Counter(
    "http_errors",
    "Count of error HTTP responses grouped by status code and route template.",
    ["status_code", "path"],
    registry=registry,
)
