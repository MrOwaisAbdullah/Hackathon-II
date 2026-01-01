"""Common dependencies for API endpoints."""
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.db.session import get_session
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# Service instance
auth_service = AuthService()


# Database session dependency
SessionDep = Annotated[Session, Depends(get_session)]


async def get_current_user(
    request: Request,
    session: SessionDep,
) -> User:
    """
    Get current authenticated user from JWT token.

    User info is extracted from token by middleware.
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
    user = auth_service.get_user_by_id(user_id, agency_id, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


async def get_current_user_from_token(request: Request, session: SessionDep) -> User:
    """Alias for get_current_user for compatibility."""
    return await get_current_user(request, session)


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_admin(current_user: CurrentUser) -> User:
    """Require user to have admin role."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
