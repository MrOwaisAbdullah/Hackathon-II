"""Integration tests for RAG service (T049).

Tests RAG retrieval with sample queries and verifies:
- Top 5 results contain relevant information
- Source references are correctly extracted
- Search threshold (0.7) filters low-quality matches
"""
import pytest
import asyncio
from app.services.rag_service import RAGService, SearchResult
from app.core.config import settings


@pytest.mark.asyncio
class TestRAGRetrieval:
    """Test RAG knowledge base retrieval functionality."""

    @pytest.fixture
    def rag_service(self):
        """Create RAG service instance."""
        return RAGService(
            qdrant_url=settings.qdrant_url,
            qdrant_api_key=settings.qdrant_api_key,
            openrouter_api_key=settings.openrouter_api_key,
        )

    def test_collection_exists(self, rag_service):
        """T049: Verify Qdrant collection exists and has data."""
        stats = rag_service.get_collection_stats()
        assert stats["status"] == "available", f"Collection not available: {stats}"
        assert stats["points_count"] > 0, "Collection is empty - run knowledge base ingestion first"

    def test_search_constitution_query(self, rag_service):
        """T049: Test query about constitution returns accurate policy explanation."""
        results = rag_service.search_knowledge_base(
            query="How do we handle authentication errors?",
            limit=5,
            score_threshold=0.7,
        )

        # Should find relevant results
        assert len(results) > 0, "No results found for constitution query"

        # Verify results have high relevance scores
        for result in results:
            assert result.score >= 0.7, f"Result below threshold: {result.score}"
            assert "auth" in result.text.lower() or "error" in result.text.lower(), \
                f"Result doesn't match query: {result.text[:100]}"

    def test_search_design_requirements(self, rag_service):
        """T049: Test query about design requirements returns relevant sections."""
        results = rag_service.search_knowledge_base(
            query="What were the design requirements for the landing page?",
            limit=5,
        )

        # Should find relevant results
        assert len(results) > 0, "No results found for design query"

        # Verify source references are extracted (T044)
        for result in results:
            assert result.source, "Source reference missing"
            assert result.title, "Title missing"
            assert 0 <= result.chunk_index < result.total_chunks, "Invalid chunk index"

    def test_search_with_no_results(self, rag_service):
        """T046: Test query with no relevant results returns empty list."""
        results = rag_service.search_knowledge_base(
            query="quantum physics theory of everything",  # Unrelated to TeamFlow
            limit=5,
        )

        # Should return empty list for unrelated queries
        assert len(results) == 0, "Should not return results for unrelated queries"

    def test_search_by_source(self, rag_service):
        """Test filtering results by source document."""
        # First, get any result to find a valid source
        all_results = rag_service.search_knowledge_base(
            query="TeamFlow",
            limit=1,
        )

        if all_results:
            source = all_results[0].source

            # Search filtered by that source
            filtered_results = rag_service.search_by_source(
                query="TeamFlow features",
                source_filter=source,
                limit=5,
            )

            # All results should be from the specified source
            for result in filtered_results:
                assert result.source == source, f"Source mismatch: {result.source} != {source}"

    def test_format_rag_context(self, rag_service):
        """T042, T044, T045: Test RAG context formatting with source references."""
        # Create sample search results
        sample_results = [
            SearchResult(
                text="TeamFlow is a CRM for creative agencies.",
                source="README.md",
                title="README",
                chunk_index=0,
                total_chunks=1,
                score=0.85,
            ),
            SearchResult(
                text="Authentication uses Better Auth.",
                source="CLAUDE.md",
                title="Constitution",
                chunk_index=5,
                total_chunks=10,
                score=0.78,
            ),
        ]

        context = rag_service.format_rag_context(
            search_results=sample_results,
            query="How does authentication work?",
        )

        # Verify context structure
        assert context["has_results"] is True
        assert len(context["sources"]) == 2
        assert "TeamFlow" in context["context_text"]
        assert "authentication" in context["context_text"].lower()

        # Verify source references (T044)
        for source in context["sources"]:
            assert "title" in source
            assert "source" in source
            assert "chunk_index" in source
            assert "score" in source

    def test_format_rag_context_no_results(self, rag_service):
        """T046: Test context formatting when no results found."""
        context = rag_service.format_rag_context(
            search_results=[],
            query="unrelated query",
        )

        # Verify no results handling
        assert context["has_results"] is False
        assert len(context["sources"]) == 0
        assert len(context["suggestions"]) > 0, "Should provide suggestions for no results"
