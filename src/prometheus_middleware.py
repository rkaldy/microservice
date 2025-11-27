from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.metrics import http_error_counter


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        try:
            response = await call_next(request)
        except Exception:
            http_error_counter.labels(status_code="500", path=path).inc()
            raise

        status_code = response.status_code
        if 400 <= status_code < 600:
            http_error_counter.labels(status_code=str(status_code), path=path).inc()
        return response
