"""Authentication endpoints - signup, login, logout."""
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from app.models.agency import AgencyCreate, AgencyRead
from app.models.user import (
    UserCreate,
    UserLogin,
    UserRead,
    UserRole,
)
from app.services.auth_service import AuthService

from app.core.memory_db import db as memory_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Test credentials bypass (for development without database)
TEST_EMAIL = "admin@test.com"
TEST_PASSWORD = "password123"
TEST_AGENCY_ID = UUID("00000000-0000-0000-0000-000000000001")
TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/signup", response_model=dict)
async def signup(
    agency_data: AgencyCreate,
    user_data: UserCreate,
) -> dict:
    """Register a new agency with admin user."""
    # Create agency in memory
    agency = await memory_db.create_agency(agency_data)

    # Create admin user in memory
    auth_service = AuthService()
    user = await auth_service.register(
        user_data,
        role=UserRole.ADMIN,
        agency_id=agency.id,
    )

    # Generate JWT token for the new user
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


@router.post("/login")
async def login(
    credentials: UserLogin,
) -> dict:
    """Authenticate user and return JWT token."""
    # === TEST BYPASS: For development without database ===
    if credentials.email == TEST_EMAIL and credentials.password == TEST_PASSWORD:
        from app.core.security import create_access_token

        # Mock test user
        test_user_data = {
            "id": str(TEST_USER_ID),
            "name": "Test Admin",
            "email": TEST_EMAIL,
            "role": "admin",
            "agency_id": str(TEST_AGENCY_ID),
        }

        token = create_access_token(
            data={
                "sub": str(TEST_USER_ID),
                "agency_id": str(TEST_AGENCY_ID),
                "email": TEST_EMAIL,
                "role": "admin",
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": test_user_data,
        }
    # === END TEST BYPASS ===

    # Get user from memory (will search all agencies)
    user = await memory_db.get_user_by_email(credentials.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Verify password
    from app.core.security import verify_password

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
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
        "access_token": token,
        "token_type": "bearer",
        "user": UserRead.model_validate(user).model_dump(),
    }


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
async def get_current_user(
    request: Request,
) -> UserRead:
    """Get current authenticated user."""
    # Get user_id from request state (set by middleware)
    user_id = request.state.user_id
    agency_id = request.state.agency_id

    # === TEST BYPASS: Handle test user ===
    if user_id == str(TEST_USER_ID) and agency_id == str(TEST_AGENCY_ID):
        return UserRead(
            id=TEST_USER_ID,
            name="Test Admin",
            email=TEST_EMAIL,
            role=UserRole.ADMIN,
            agency_id=TEST_AGENCY_ID,
        )
    # === END TEST BYPASS ===

    # Get user from memory
    user = await memory_db.get_user_by_id(UUID(user_id), UUID(agency_id))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead.model_validate(user)
