"""In-memory database for testing without PostgreSQL."""
from typing import Dict, List, Optional
from uuid import UUID

from app.models.agency import Agency, AgencyCreate
from app.models.user import User, UserCreate, UserRole


class InMemoryDatabase:
    """Simple in-memory database for testing."""

    def __init__(self) -> None:
        self.agencies: Dict[UUID, Agency] = {}
        self.users: Dict[UUID, User] = {}
        self.users_by_email: Dict[str, UUID] = {}

    async def create_agency(self, agency_data: AgencyCreate) -> Agency:
        """Create an agency."""
        agency = Agency(**agency_data.model_dump())
        self.agencies[agency.id] = agency
        return agency

    async def get_agency_by_id(self, agency_id: UUID) -> Optional[Agency]:
        """Get agency by ID."""
        return self.agencies.get(agency_id)

    async def create_user(
        self,
        user_data: UserCreate,
        agency_id: UUID,
        hashed_password: str,
        role: UserRole | None = None,
    ) -> User:
        """Create a user."""
        existing_user_id = self.users_by_email.get(f"{user_data.email}:{agency_id}")
        if existing_user_id:
            raise ValueError("User with this email already exists in agency")

        user = User(
            **user_data.model_dump(exclude={"password", "role"}),
            hashed_password=hashed_password,
            agency_id=agency_id,
            role=role or user_data.role,
        )
        self.users[user.id] = user
        self.users_by_email[f"{user.email}:{agency_id}"] = user.id
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (searches all agencies)."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def get_user_by_id(self, user_id: UUID, agency_id: UUID) -> Optional[User]:
        """Get user by ID within an agency."""
        user = self.users.get(user_id)
        if user and user.agency_id == agency_id:
            return user
        return None


db = InMemoryDatabase()
