"""Performance tests for RAG queries (T056).

Verifies that RAG queries return within 3 seconds (SC-003).
"""
import pytest
import time
import asyncio
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
class TestRAGPerformance:
    """Performance tests for RAG chat API responses."""

    @pytest.fixture
    async def client(self):
        """Create async HTTP client."""
        async with AsyncClient(base_url=settings.api_v1_prefix) as ac:
            yield ac

    @pytest.fixture
    async def conversation_id(self, client: AsyncClient):
        """Create a test conversation and return its ID."""
        response = await client.post(
            "/chat/sessions",
            json={"user_id": "test-user-performance"},
        )
        assert response.status_code == 200
        data = response.json()
        return data["conversation_id"]

    @pytest.mark.asyncio
    async def test_rag_query_performance_constitution(self, client: AsyncClient, conversation_id: str):
        """T056: Verify RAG query for constitution returns within 3 seconds (SC-003)."""
        query = "How do we handle authentication errors?"

        start_time = time.time()

        response = await client.post(
            "/chat/respond",
            json={
                "message": query,
                "conversation_id": conversation_id,
                "user_id": "test-user",
            },
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify response is successful
        assert response.status_code == 200

        # SC-003: Verify response time is under 3 seconds
        assert elapsed < 3.0, f"RAG query took {elapsed:.2f}s, exceeds 3s threshold (SC-003)"

        # Verify response contains relevant content
        data = response.json()
        assert "response" in data or "content" in data

    @pytest.mark.asyncio
    async def test_rag_query_performance_design(self, client: AsyncClient, conversation_id: str):
        """T056: Verify RAG query for design requirements returns within 3 seconds."""
        query = "What are the design requirements for the landing page?"

        start_time = time.time()

        response = await client.post(
            "/chat/respond",
            json={
                "message": query,
                "conversation_id": conversation_id,
                "user_id": "test-user",
            },
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify response is successful
        assert response.status_code == 200

        # SC-003: Verify response time is under 3 seconds
        assert elapsed < 3.0, f"RAG query took {elapsed:.2f}s, exceeds 3s threshold (SC-003)"

    @pytest.mark.asyncio
    async def test_multiple_rag_queries_performance(self, client: AsyncClient):
        """T056: Test multiple consecutive RAG queries all under 3 seconds."""
        queries = [
            "How do we handle authentication errors?",
            "What are the design requirements for the landing page?",
            "How does the task assignment work?",
            "Explain the project structure",
            "What is the database schema?",
        ]

        # Create conversation
        response = await client.post(
            "/chat/sessions",
            json={"user_id": "test-user-multi"},
        )
        assert response.status_code == 200
        conversation_id = response.json()["conversation_id"]

        # Test each query
        for i, query in enumerate(queries):
            start_time = time.time()

            response = await client.post(
                "/chat/respond",
                json={
                    "message": query,
                    "conversation_id": conversation_id,
                    "user_id": "test-user",
                },
            )

            end_time = time.time()
            elapsed = end_time - start_time

            assert response.status_code == 200, f"Query {i+1} failed"
            assert elapsed < 3.0, f"Query {i+1} took {elapsed:.2f}s, exceeds 3s threshold (SC-003)"

    @pytest.mark.asyncio
    async def test_session_creation_performance(self, client: AsyncClient):
        """Verify session creation is fast (should be < 500ms)."""
        start_time = time.time()

        response = await client.post(
            "/chat/sessions",
            json={"user_id": "test-user-session-perf"},
        )

        end_time = time.time()
        elapsed = end_time - start_time

        assert response.status_code == 200
        assert elapsed < 0.5, f"Session creation took {elapsed:.2f}s, should be < 500ms"

    @pytest.mark.asyncio
    async def test_message_history_performance(self, client: AsyncClient):
        """Verify message history retrieval is fast."""
        # Create conversation
        response = await client.post(
            "/chat/sessions",
            json={"user_id": "test-user-history-perf"},
        )
        conversation_id = response.json()["conversation_id"]

        start_time = time.time()

        response = await client.get(f"/chat/conversations/{conversation_id}/messages")

        end_time = time.time()
        elapsed = end_time - start_time

        assert response.status_code == 200
        assert elapsed < 0.5, f"History retrieval took {elapsed:.2f}s, should be < 500ms"
