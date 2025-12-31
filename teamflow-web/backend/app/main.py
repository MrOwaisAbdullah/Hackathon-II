"""FastAPI application for TeamFlow backend."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth
from app.core.config import settings


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
