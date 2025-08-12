import uuid
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url} [{request_id}]")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(f"Request completed: {response.status_code} [{request_id}] {duration:.3f}s")
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed: {str(e)} [{request_id}] {duration:.3f}s")
            raise


def get_request_id(request: Request) -> str:
    return getattr(request.state, 'request_id', 'no-request-id')
