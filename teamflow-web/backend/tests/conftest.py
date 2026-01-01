"""Pytest configuration and fixtures."""
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def session() -> Generator[Session, None, None]:
    """Fixture for database session.

    Creates an in-memory SQLite database for each test function.
    """
    from app.models import Agency, User  # noqa: F401
    from app.db.session import engine

    # Create test engine with in-memory SQLite
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create tables
    SQLModel.metadata = Agency.metadata  # type: ignore
    SQLModel.metadata.create_all(test_engine)  # type: ignore

    # Create session
    with Session(test_engine) as session:
        yield session

    # Drop tables after test
    SQLModel.metadata.drop_all(test_engine)  # type: ignore


# Import SQLModel after models are loaded
from sqlmodel import SQLModel


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture for async HTTP client (alias for async_client)."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture for async HTTP client."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
