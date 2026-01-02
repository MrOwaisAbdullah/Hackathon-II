"""Authentication endpoints - signup, login, logout."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from app.db.session import SessionDep, get_session
from app.models.agency import AgencyCreate, AgencyRead
from app.models.user import (
    UserCreate,
    UserLogin,
    UserRead,
    UserRole,
)
from app.services.auth_service import AuthService
from app.core.rate_limit import check_rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Service instance
auth_service = AuthService()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(
    agency_data: AgencyCreate,
    user_data: UserCreate,
    session: SessionDep,
    request: Request,
) -> dict:
    """
    Register a new agency with admin user.

    This endpoint creates both an agency and the first admin user for that agency.
    """
    # T163: Rate limiting check (3 registrations per hour per IP)
    check_rate_limit(request, "auth_register")

    # Create agency
    agency = auth_service.register_agency(agency_data, session)

    # Create admin user for the agency
    user = auth_service.register_user(
        user_data,
        agency_id=agency.id,
        session=session,
        role=UserRole.admin,
    )

    # Generate JWT token
    from app.core.security import create_access_token

    token = create_access_token(
        data={
            "sub": str(user.id),
            "agency_id": str(user.agency_id),
            "email": user.email,
            "role": user.role.value,
        }
    )

    return {
        "agency": AgencyRead.model_validate(agency).model_dump(),
        "user": UserRead.model_validate(user).model_dump(),
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=dict)
def login(
    credentials: UserLogin,
    session: SessionDep,
    request: Request,
) -> dict:
    """Authenticate user and return JWT token."""
    # T163: Rate limiting check (5 login attempts per minute per IP)
    check_rate_limit(request, "auth_login")

    try:
        user, token = auth_service.login(credentials, session)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserRead.model_validate(user).model_dump(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
def logout() -> dict[str, str]:
    """
    Logout user.

    JWT tokens are stateless - logout is handled client-side by removing the token.
    This endpoint exists for API completeness and future token blacklisting.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
def get_current_user(
    request: Request,
    session: SessionDep,
) -> UserRead:
    """
    Get current authenticated user.

    Requires valid JWT token. User info is extracted from token by middleware.
    """
    # Get user_id from request state (set by JWT middleware)
    user_id = getattr(request.state, "user_id", None)
    agency_id = getattr(request.state, "agency_id", None)

    if not user_id or not agency_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Get user from database (scoped to agency for multi-tenant isolation)
    user = auth_service.get_user_by_id(UUID(user_id), UUID(agency_id), session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserRead.model_validate(user)
