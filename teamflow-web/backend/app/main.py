"""FastAPI application for TeamFlow backend."""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware

from app.api.endpoints import auth, analytics, projects, tasks, time_entries, users
from app.api.endpoints import chat
from app.core.config import settings
from app.core.logging import get_logger, RequestLoggingMiddleware

# T155: Use structured logger
logger = get_logger(__name__)

# T086: Global scheduler for background tasks
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager (T086)."""

    async def run_cleanup_job():
        """Background task to run cleanup job."""
        try:
            from app.jobs.cleanup_conversations import main as cleanup_main
            logger.info("[lifespan] Running scheduled conversation cleanup job")
            # Run cleanup in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, cleanup_main)
            logger.info("[lifespan] Cleanup job completed")
        except Exception as e:
            logger.error(f"[lifespan] Cleanup job failed: {str(e)}")

    # Startup
    logger.info("[lifespan] Starting up application...")

    # T086: Schedule cleanup job to run daily at 2 AM UTC
    scheduler.add_job(
        run_cleanup_job,
        'cron',
        hour=2,
        minute=0,
        id='cleanup_conversations',
        name='Daily conversation cleanup',
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[lifespan] Scheduler started - cleanup job scheduled for daily 2 AM UTC")

    yield

    # Shutdown
    logger.info("[lifespan] Shutting down application...")
    scheduler.shutdown()
    logger.info("[lifespan] Scheduler stopped")


app = FastAPI(
    title="TeamFlow API",
    description="TeamFlow Phase 2: Full-Stack Agency CRM Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# T162: GZip compression middleware (compresses responses > 1000 bytes)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# T155: Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(tasks.router, prefix=settings.api_v1_prefix)
app.include_router(projects.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(time_entries.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(chat.router, prefix=settings.api_v1_prefix)  # Phase 3: Chat endpoints


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "teamflow-backend"}


# T093: Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for uptime monitoring (T093).

    Exposes metrics in Prometheus text format for scraping.
    Metrics include:
    - Chat service health and performance
    - AI agent response times
    - RAG search performance
    - MCP tool execution
    - System uptime and health

    Returns:
        Prometheus metrics in text format
    """
    from fastapi.responses import Response
    from app.core.metrics import get_metrics, CONTENT_TYPE_LATEST

    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# JWT Middleware - extracts user info from token and adds to request state
@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    """Middleware to verify JWT token and extract user info."""
    from app.core.security import decode_access_token

    # Skip auth for health check and OPTIONS
    if request.url.path == "/health" or request.method == "OPTIONS":
        return await call_next(request)

    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ")
        payload = decode_access_token(token)
        if payload:
            request.state.user_id = payload.get("sub")
            request.state.agency_id = payload.get("agency_id")
            request.state.email = payload.get("email")
            request.state.role = payload.get("role")

    return await call_next(request)


# T155: Error handling middleware with structured logging
# T089: Standardized error response format
# T090: Comprehensive error logging with context
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors (T089, T090)."""
    error_context = {
        "method": request.method,
        "path": str(request.url.path),
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "user_id": getattr(request.state, "user_id", None),
        "agency_id": getattr(request.state, "agency_id", None),
        "email": getattr(request.state, "email", None),
        "role": getattr(request.state, "role", None),
        "headers": dict(request.headers),
    }

    logger.error(
        "[global_exception_handler] Unhandled exception",
        **error_context,
    )

    # T089: Standardized error response format
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.environment != "production" else None,
                "timestamp": datetime.utcnow().isoformat(),
            }
        },
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_exception_handler(request: Request, exc: Exception):
    """Handle 404 errors (T089, T090)."""
    logger.warning(
        "[not_found_exception_handler] Resource not found",
        method=request.method,
        path=str(request.url.path),
        user_id=getattr(request.state, "user_id", None),
    )

    # T089: Standardized error response format
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested resource was not found",
                "details": {"path": str(request.url.path)},
                "timestamp": datetime.utcnow().isoformat(),
            }
        },
    )


@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
async def validation_exception_handler(request: Request, exc: Exception):
    """Handle validation errors (T089, T090)."""
    logger.warning(
        "[validation_exception_handler] Validation error",
        method=request.method,
        path=str(request.url.path),
        error_message=str(exc),
        user_id=getattr(request.state, "user_id", None),
    )

    # T089: Standardized error response format
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": str(exc) if settings.environment != "production" else None,
                "timestamp": datetime.utcnow().isoformat(),
            }
        },
    )


@app.exception_handler(status.HTTP_429_TOO_MANY_REQUESTS)
async def rate_limit_exception_handler(request: Request, exc: Exception):
    """Handle rate limit errors (T089, T090)."""
    logger.warning(
        "[rate_limit_exception_handler] Rate limit exceeded",
        method=request.method,
        path=str(request.url.path),
        user_id=getattr(request.state, "user_id", None),
    )

    # T089: Standardized error response format for rate limiting
    # Rate limit headers are already added by the rate_limit function
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "details": getattr(request.state, "rate_limit_info", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }
        },
    )
