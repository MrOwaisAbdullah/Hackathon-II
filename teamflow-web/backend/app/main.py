"""FastAPI application for TeamFlow backend.

MCP server is mounted at /mcp using FastAPI's mount() method.
Key configuration: streamable_http_path="/" and json_response=True
must be set during FastMCP() initialization (see app/mcp/server.py).
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.middleware.gzip import GZipMiddleware

from app.api.endpoints import auth, analytics, projects, tasks, time_entries, users
from app.api.endpoints import chat
from app.core.config import settings
from app.core.logging import get_logger, RequestLoggingMiddleware

# Import MCP server for mounting in FastAPI (single-server architecture)
from app.mcp.server import mcp

# T155: Use structured logger
logger = get_logger(__name__)

# T086: Global scheduler for background tasks
scheduler = AsyncIOScheduler()


# ============================================================================
# Lifespan Management
# ============================================================================

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
    logger.info("[lifespan] MCP server available at /mcp endpoint")

    # Start MCP session manager (required for streamable HTTP transport)
    async with mcp.session_manager.run():
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

    # Stop scheduler
    scheduler.shutdown()
    logger.info("[lifespan] Scheduler stopped")
    logger.info("[lifespan] Application shutdown complete")


# ============================================================================
# Create FastAPI Application with MCP server mounted
# ============================================================================

# Create FastAPI application with lifespan
app = FastAPI(
    lifespan=lifespan,
    title="TeamFlow Backend",
    description="TeamFlow project management backend API",
    version="1.0.0",
)

# Include all API routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(tasks.router, prefix=settings.api_v1_prefix)
app.include_router(projects.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(time_entries.router, prefix=settings.api_v1_prefix)
app.include_router(analytics.router, prefix=settings.api_v1_prefix)
app.include_router(chat.router, prefix=settings.api_v1_prefix)

# Add health and metrics endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "teamflow-backend"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for uptime monitoring (T093)."""
    from app.core.metrics import get_metrics, CONTENT_TYPE_LATEST

    metrics_data = get_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Mount MCP server at /mcp endpoint
# CRITICAL: streamable_http_path="/" and json_response=True must be set
# during FastMCP() initialization (see app/mcp/server.py)
app.mount("/mcp", mcp.streamable_http_app(), name="mcp")

# Add middleware to the app
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================

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
    }

    logger.error(
        "[global_exception_handler] Unhandled exception",
        **error_context,
    )

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


# ============================================================================
# JWT Middleware
# ============================================================================

@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    """Middleware to verify JWT token and extract user info."""
    from app.core.security import decode_access_token

    # Skip auth for health check, metrics, OPTIONS, and MCP endpoint
    if request.url.path in ["/health", "/metrics", "/mcp"] or request.method == "OPTIONS":
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


logger.info("FastAPI application created with MCP server mounted at /mcp endpoint")
logger.info(f"MCP server configuration: streamable_http_path='/', json_response=True")
