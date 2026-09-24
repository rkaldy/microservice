from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.metrics import http_error_counter

UNMATCHED_ROUTE_TEMPLATE = "unmatched"


def get_route_template(request: Request) -> str:
    """Return the matched route template without recording the concrete URL path."""
    route = request.scope.get("route")
    return getattr(route, "path", UNMATCHED_ROUTE_TEMPLATE)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
        except Exception:
            http_error_counter.labels(status_code="500", path=get_route_template(request)).inc()
            raise

        status_code = response.status_code
        if 400 <= status_code < 600:
            http_error_counter.labels(
                status_code=str(status_code), path=get_route_template(request)
            ).inc()
        return response
