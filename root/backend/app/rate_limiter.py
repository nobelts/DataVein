import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Get client IP for rate limiting, handles proxies"""
    # Check for forwarded headers first (when behind proxy)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Fall back to direct connection IP
    if request.client:
        return request.client.host
    
    return "127.0.0.1"


# Create limiter instance
# Uses in-memory storage for MVP (Redis can be added later for production)
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=os.getenv("REDIS_URL", "memory://"),  # Falls back to memory if no Redis
    default_limits=["200/minute"]  # Global default limit
)


def setup_rate_limiting(app):
    """Setup rate limiting for FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
