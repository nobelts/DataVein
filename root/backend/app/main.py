"""
DataVein API - Data Processing Platform Backend
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.uploads import router as uploads_router
from app.api.pipeline import router as pipeline_router
from app.logging_middleware import LoggingMiddleware, get_request_id
from app.rate_limiter import setup_rate_limiting
from app.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DataVein API",
    description="Data processing platform with secure file uploads",
    version="1.0.0"
)

# Setup rate limiting
setup_rate_limiting(app)

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(uploads_router)
app.include_router(pipeline_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting DataVein API")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": get_request_id(request)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": get_request_id(request)
        }
    )


@app.get("/")
async def read_root():
    return {
        "message": "DataVein API",
        "version": "1.0.0",
        "docs": "/docs"
    }