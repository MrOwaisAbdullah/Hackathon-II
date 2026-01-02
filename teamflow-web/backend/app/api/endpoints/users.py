"""Users API endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, SessionDep
from app.models.user import User, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()


@router.get("", response_model=List[UserRead])
def list_users(
    current_user: CurrentUser,
    session: SessionDep,
) -> List[User]:
    """List all users in the current agency (team members)."""
    return user_service.list_users(current_user.agency_id, session)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> User:
    """Get a user by ID (scoped to current agency)."""
    user = user_service.get_user(str(user_id), current_user.agency_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
