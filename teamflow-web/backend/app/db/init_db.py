"""Database initialization utilities for TeamFlow backend."""
import logging
from uuid import uuid4

from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.models.agency import Agency
from app.models.user import User, UserRole

# Import models to ensure they're registered with SQLModel.metadata
# This is required for SQLModel.metadata.create_all() to discover tables
from app.db.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize database tables.

    This function creates all tables defined in SQLModel classes.
    Use this for development/testing - use Alembic migrations for production.
    """
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def create_test_agency(session: Session) -> Agency:
    """Create a test agency for development."""
    agency = Agency(
        id=uuid4(),
        name="Test Agency",
        email="test@agency.com",
    )
    session.add(agency)
    session.commit()
    session.refresh(agency)
    logger.info(f"Created test agency: {agency.name} ({agency.id})")
    return agency


def create_test_user(session: Session, agency_id: str, email: str = "admin@test.com") -> User:
    """Create a test user for development."""
    from app.core.security import get_password_hash

    user = User(
        id=uuid4(),
        name="Admin User",
        email=email,
        hashed_password=get_password_hash("password123"),
        role=UserRole.admin,
        agency_id=agency_id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info(f"Created test user: {user.name} ({user.id})")
    return user


def seed_database(session: Session) -> None:
    """
    Seed database with initial test data.

    Creates a test agency and admin user for development purposes.
    Skip this in production - only for local development.
    """
    if settings.environment == "production":
        logger.warning("Skipping database seed in production environment")
        return

    # Check if data already exists
    existing_agency = session.exec(select(Agency).limit(1)).first()
    if existing_agency:
        logger.info("Database already seeded - skipping")
        return

    logger.info("Seeding database with test data...")
    agency = create_test_agency(session)
    create_test_user(session, str(agency.id))
    logger.info("Database seeding complete")


def reset_database(session: Session) -> None:
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data. Only use in development/testing.
    Never call this in production!
    """
    if settings.environment == "production":
        raise RuntimeError("Cannot reset database in production environment")

    logger.warning("Resetting database - all data will be lost")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    logger.info("Database reset complete")


# CLI entry point for running initialization
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()

    # Optionally seed with test data
    with Session(engine) as session:
        seed_database(session)
