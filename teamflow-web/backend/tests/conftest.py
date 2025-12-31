"""Pytest configuration and fixtures."""
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture for async HTTP client."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
