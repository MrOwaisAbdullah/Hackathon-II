"""Authentication service using in-memory database for testing."""
from typing import Optional
from uuid import UUID

from app.core.memory_db import db
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserCreate, UserLogin, UserRole


class AuthService:
    """Service for authentication operations using in-memory database."""

    async def register(
        self,
        user_data: UserCreate,
        agency_id: UUID,
        role: UserRole | None = None,
    ) -> User:
        """Register a new user within an agency."""
        hashed_password = get_password_hash(user_data.password)
        user = await db.create_user(user_data, agency_id, hashed_password, role)
        return user

    async def login(self, credentials: UserLogin) -> tuple[User, str]:
        """Authenticate user and generate JWT token."""
        user = await db.get_user_by_email(credentials.email)

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        token = create_access_token(
            data={
                "sub": str(user.id),
                "agency_id": str(user.agency_id),
                "email": user.email,
                "role": user.role.value,
            }
        )

        return user, token

    async def get_user_by_id(self, user_id: UUID, agency_id: UUID) -> Optional[User]:
        """Get user by ID within an agency."""
        return await db.get_user_by_id(user_id, agency_id)
