"""Authentication service using SQLModel database."""
from typing import Optional
from uuid import UUID

from sqlmodel import Session, col, select

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.agency import Agency, AgencyCreate
from app.models.user import User, UserCreate, UserLogin, UserRole


class AuthService:
    """Service for authentication operations using SQLModel database."""

    def register_agency(
        self,
        agency_data: AgencyCreate,
        session: Session,
    ) -> Agency:
        """Register a new agency."""
        # Check if agency email already exists
        existing = session.exec(
            select(Agency).where(Agency.email == agency_data.email)
        ).first()
        if existing:
            raise ValueError("Agency with this email already exists")

        agency = Agency.model_validate(agency_data)
        session.add(agency)
        session.commit()
        session.refresh(agency)
        return agency

    def register_user(
        self,
        user_data: UserCreate,
        agency_id: UUID,
        session: Session,
        role: UserRole | None = None,
    ) -> User:
        """Register a new user within an agency."""
        # Check if user email already exists in this agency
        existing = session.exec(
            select(User).where(
                col(User.email) == user_data.email,
                User.agency_id == agency_id
            )
        ).first()
        if existing:
            raise ValueError("User with this email already exists in agency")

        hashed_password = get_password_hash(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            agency_id=agency_id,
            role=role or user_data.role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def login(self, credentials: UserLogin, session: Session) -> tuple[User, str]:
        """Authenticate user and generate JWT token."""
        user = session.exec(
            select(User).where(col(User.email) == credentials.email)
        ).first()

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

    def get_user_by_id(self, user_id: UUID, agency_id: UUID, session: Session) -> Optional[User]:
        """Get user by ID within an agency (scoped to agency for multi-tenant isolation)."""
        return session.exec(
            select(User).where(
                User.id == user_id,
                User.agency_id == agency_id
            )
        ).first()

    def get_agency_users(self, agency_id: UUID, session: Session) -> list[User]:
        """Get all users in an agency."""
        return session.exec(
            select(User).where(User.agency_id == agency_id)
        ).all()
