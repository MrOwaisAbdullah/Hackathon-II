"""Users API endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.core.deps import CurrentUser, SessionDep
from app.core.logging import get_logger, log_api_call
from app.core.rate_limit import check_rate_limit
from app.models.user import User, UserRead, UserRole
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()
logger = get_logger("api.users")


# Request schemas
class UserCreateRequest(BaseModel):
    """User creation request."""
    name: str = Field(..., min_length=1, max_length=100)
    email: str  # Changed from EmailStr to allow .local domains
    role: UserRole = UserRole.member
    is_project_manager: bool = False


class UserUpdateRequest(BaseModel):
    """User update request (all fields optional)."""
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None  # Changed from EmailStr to allow .local domains
    role: UserRole | None
    is_project_manager: bool | None


class UserReadWithTempPassword(UserRead):
    """User read response with temporary password (only on create)."""
    temp_password: str | None = None


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


@router.post("", response_model=UserReadWithTempPassword, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateRequest,
    current_user: CurrentUser,
    session: SessionDep,
    request: Request,
) -> User:
    """Create a new user (admin only).

    Generates a temporary password that expires in 24 hours.
    The user will be required to change it on first login.
    """
    # T186: Rate limiting check (10 user creations per hour per agency)
    check_rate_limit(request, "users_create")
    # Convert request to UserCreate
    from app.models.user import UserCreate
    user_create = UserCreate(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        is_project_manager=user_data.is_project_manager,
    )

    user, temp_password = user_service.create_user(
        user_create,
        current_user.agency_id,
        session,
        current_user,
    )

    # Audit log: User created
    log_api_call(
        logger,
        endpoint="POST /api/v1/users",
        action="create_user",
        user_id=str(current_user.id),
        agency_id=str(current_user.agency_id),
        target_user_id=str(user.id),
        target_user_email=user.email,
        target_user_role=user.role.value,
        is_project_manager=user.is_project_manager,
    )

    # Return user with temp password
    response_data = UserReadWithTempPassword(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        agency_id=user.agency_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
        temp_password=temp_password,
    )
    return response_data


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    user_data: UserUpdateRequest,
    current_user: CurrentUser,
    session: SessionDep,
    request: Request,
) -> User:
    """Update a user (admin only).

    Allows updating: name, email, role, is_project_manager.
    Password changes are handled separately.
    """
    # T186: Rate limiting check (30 user updates per minute per agency)
    check_rate_limit(request, "users_update")
    # Convert request to UserUpdate (only include non-None fields)
    from app.models.user import UserUpdate
    update_data = UserUpdate(
        **{k: v for k, v in user_data.model_dump().items() if v is not None}
    )

    updated_user = user_service.update_user(
        str(user_id),
        update_data,
        current_user.agency_id,
        session,
        current_user,
    )

    # Audit log: User updated
    log_api_call(
        logger,
        endpoint=f"PATCH /api/v1/users/{user_id}",
        action="update_user",
        user_id=str(current_user.id),
        agency_id=str(current_user.agency_id),
        target_user_id=str(updated_user.id),
        updated_fields=list(update_data.model_dump(exclude_unset=True).keys()),
    )

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
    request: Request,
) -> None:
    """Delete a user (admin only).

    Performs a soft delete (sets active=False).
    The user's tasks will become unassigned.
    Cannot delete the last admin or yourself.
    """
    # T186: Rate limiting check (5 user deletions per hour per agency)
    check_rate_limit(request, "users_delete")
    # Get user info before deletion for audit log
    from app.models.user import User
    target_user = session.get(User, str(user_id))

    user_service.delete_user(
        str(user_id),
        current_user.agency_id,
        session,
        current_user,
    )

    # Audit log: User deleted
    log_api_call(
        logger,
        endpoint=f"DELETE /api/v1/users/{user_id}",
        action="delete_user",
        user_id=str(current_user.id),
        agency_id=str(current_user.agency_id),
        target_user_id=str(user_id),
        target_user_email=target_user.email if target_user else None,
    )
