"""RAG service for knowledge base semantic search (T014).

LangChain-free implementation using:
- OpenRouter API for query embeddings (via OpenAI SDK)
- Qdrant client for vector similarity search
- Configurable search threshold (0.7 cosine similarity)
"""
from typing import List, Optional
from dataclasses import dataclass
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, ScoredPoint

from app.core.config import settings


@dataclass
class SearchResult:
    """A single search result from the knowledge base."""

    text: str
    source: str
    title: str
    chunk_index: int
    total_chunks: int
    score: float

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "text": self.text,
            "source": self.source,
            "title": self.title,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "score": self.score,
        }


class RAGService:
    """Service for RAG knowledge base operations."""

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        collection_name: str = "teamflow_kb",
        search_threshold: float = 0.7,
    ):
        self.qdrant_client = QdrantClient(
            url=qdrant_url or settings.qdrant_url,
            api_key=qdrant_api_key or settings.qdrant_api_key,
        )
        # Use OpenRouter for embeddings (OpenAI-compatible API)
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key or settings.openrouter_api_key,
        )
        self.collection_name = collection_name
        self.search_threshold = search_threshold
        # Use OpenAI text-embedding-3-small via OpenRouter ($0.02/1M tokens)
        self.embedding_model = "openai/text-embedding-3-small"

    def _embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query using OpenRouter."""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=[query],
        )
        return response.data[0].embedding

    def search_knowledge_base(
        self,
        query: str,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """Search the knowledge base using semantic similarity.

        Args:
            query: Natural language query text
            limit: Maximum number of results to return (default: 5)
            score_threshold: Minimum cosine similarity score (default: 0.7)

        Returns:
            List of SearchResult objects with text, metadata, and scores
        """
        threshold = score_threshold or self.search_threshold

        # Generate query embedding
        query_embedding = self._embed_query(query)

        # Search Qdrant
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
        )

        # Convert to SearchResult objects
        results = []
        for result in search_results:
            if result.score >= threshold:
                results.append(
                    SearchResult(
                        text=result.payload.get("text", ""),
                        source=result.payload.get("source", ""),
                        title=result.payload.get("title", ""),
                        chunk_index=result.payload.get("chunk_index", 0),
                        total_chunks=result.payload.get("total_chunks", 1),
                        score=result.score,
                    )
                )

        return results

    def search_by_source(
        self,
        query: str,
        source_filter: str,
        limit: int = 5,
    ) -> List[SearchResult]:
        """Search knowledge base filtered by source document.

        Args:
            query: Natural language query text
            source_filter: Filter results to only this source file
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects from the specified source
        """
        # Generate query embedding
        query_embedding = self._embed_query(query)

        # Search with source filter
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source_filter),
                    )
                ]
            ),
            limit=limit,
            score_threshold=self.search_threshold,
        )

        # Convert to SearchResult objects
        results = []
        for result in search_results:
            results.append(
                SearchResult(
                    text=result.payload.get("text", ""),
                    source=result.payload.get("source", ""),
                    title=result.payload.get("title", ""),
                    chunk_index=result.payload.get("chunk_index", 0),
                    total_chunks=result.payload.get("total_chunks", 1),
                    score=result.score,
                )
            )

        return results

    def get_collection_stats(self) -> dict:
        """Get statistics about the knowledge base collection.

        Returns:
            Dict with collection info (point count, vector size, etc.)
        """
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "status": "available",
            }
        except Exception as e:
            return {
                "collection_name": self.collection_name,
                "status": "unavailable",
                "error": str(e),
            }
