"""FastAPI application for TeamFlow backend."""
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import auth, projects, tasks
from app.core.config import settings

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="TeamFlow API",
    description="TeamFlow Phase 2: Full-Stack Agency CRM Backend",
    version="0.1.0",
    lifespan=lifespan,
)

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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "teamflow-backend"}


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


# Error handling middleware with structured logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        f"Unhandled exception on {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
            "user_id": getattr(request.state, "user_id", None),
            "agency_id": getattr(request.state, "agency_id", None),
        }
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.environment != "production" else "An unexpected error occurred",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_exception_handler(request: Request, exc: Exception):
    """Handle 404 errors."""
    logger.warning(
        f"404 error on {request.url.path}: {str(exc)}",
        extra={
            "method": request.method,
            "path": request.url.path,
        }
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not found", "path": str(request.url.path)},
    )


@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
async def validation_exception_handler(request: Request, exc: Exception):
    """Handle validation errors."""
    logger.warning(
        f"Validation error on {request.url.path}: {str(exc)}",
        extra={
            "method": request.method,
            "path": request.url.path,
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "detail": str(exc)},
    )
