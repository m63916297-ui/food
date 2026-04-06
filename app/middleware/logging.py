import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", "N/A")

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
            client=request.client.host if request.client else "unknown"
        )

        response = await call_next(request)

        duration = time.time() - start_time
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            request_id=request_id
        )

        return response
