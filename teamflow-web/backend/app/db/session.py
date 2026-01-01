"""Database session management for TeamFlow backend."""
from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.core.config import settings

# Create database engine for Neon PostgreSQL
# SQLModel uses synchronous sessions with psycopg2 driver
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to yield database sessions.

    This pattern ensures sessions are properly closed after each request.
    Usage in FastAPI: Depends(get_session)
    """
    with Session(engine) as session:
        yield session


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
