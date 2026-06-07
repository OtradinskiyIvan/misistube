import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from .logging import bind_correlation_id


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        bind_correlation_id(correlation_id)

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
