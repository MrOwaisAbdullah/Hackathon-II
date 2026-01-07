"""Knowledge base ingestion job for TeamFlow RAG (T013).

LangChain-free implementation using:
- RecursiveTextSplitter for intelligent chunking
- OpenRouter API for embeddings (via OpenAI SDK)
- Qdrant client for vector storage
- Document metadata tracking with last_modified (T048)
- Incremental refresh logic for changed files (T047)
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime
import hashlib

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue

from app.core.config import settings


class IntelligentChunker:
    """Markdown-aware text chunker (LangChain-free)."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _protect_code_blocks(self, text: str) -> tuple[str, dict[str, str]]:
        """Protect code blocks from splitting."""
        placeholders = {}
        pattern = r'```[\s\S]*?```'

        def replace_with_placeholder(match):
            placeholder = f"__CODE_BLOCK_{len(placeholders)}__"
            placeholders[placeholder] = match.group(0)
            return placeholder

        protected_text = re.sub(pattern, replace_with_placeholder, text)
        return protected_text, placeholders

    def _restore_code_blocks(self, text: str, placeholders: dict[str, str]) -> str:
        """Restore protected code blocks in a single chunk."""
        result = text
        for placeholder, code_block in placeholders.items():
            if placeholder in result:  # Only replace if present
                result = result.replace(placeholder, code_block, 1)  # Replace only once
        return result

    def _split_text(self, text: str) -> List[str]:
        """Split text recursively by paragraphs, lines, sentences."""
        # Try splitting by paragraphs first
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        current_position = 0
        max_chunks = 10000  # Safety limit to prevent memory issues
        iterations = 0

        while current_position < len(text) and iterations < max_chunks:
            iterations += 1
            # Find the best split point
            end = min(current_position + self.chunk_size, len(text))

            # Try to split at paragraph boundary
            paragraph_split = text.rfind('\n\n', current_position, end)
            if paragraph_split > current_position:
                split_point = paragraph_split + 2
            else:
                # Try to split at line boundary
                line_split = text.rfind('\n', current_position, end)
                if line_split > current_position:
                    split_point = line_split + 1
                else:
                    # Try to split at sentence boundary
                    sentence_split = text.rfind('. ', current_position, end)
                    if sentence_split > current_position:
                        split_point = sentence_split + 2
                    else:
                        split_point = end

            # Ensure we make progress
            if split_point <= current_position:
                split_point = min(current_position + 100, len(text))

            chunk = text[current_position:split_point].strip()
            if chunk:
                chunks.append(chunk)

            # Move forward with overlap (ensure progress)
            new_position = split_point - self.overlap
            if new_position <= current_position:
                new_position = split_point  # No overlap if we can't move back
            current_position = new_position

        if iterations >= max_chunks:
            print(f"    ⚠️  Reached maximum chunk limit ({max_chunks}), truncating...")

        return chunks

    def chunk_document(self, text: str) -> List[str]:
        """Chunk a document while preserving code blocks."""
        # Protect code blocks
        protected_text, placeholders = self._protect_code_blocks(text)

        # Split text
        chunks = self._split_text(protected_text)

        # Restore code blocks
        restored_chunks = [self._restore_code_blocks(chunk, placeholders) for chunk in chunks]

        return restored_chunks


class KnowledgeBaseIngestor:
    """Ingest TeamFlow documentation into Qdrant for RAG."""

    def __init__(
        self,
        qdrant_url: str,
        qdrant_api_key: str,
        openrouter_api_key: str,
        collection_name: str = "teamflow_kb",
    ):
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        # Use OpenRouter for embeddings (OpenAI-compatible API)
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )
        self.collection_name = collection_name
        self.chunker = IntelligentChunker(chunk_size=1000, overlap=200)
        # Use OpenAI text-embedding-3-small via OpenRouter ($0.02/1M tokens)
        self.embedding_model = "openai/text-embedding-3-small"
        self.embedding_dim = 1536  # text-embedding-3-small dimension

    def _setup_collection(self):
        """Create Qdrant collection if it doesn't exist or recreate if dimension mismatch."""
        collections = self.qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.collection_name in collection_names:
            # Check if dimension matches
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            current_dim = collection_info.config.params.vectors.size
            if current_dim != self.embedding_dim:
                print(f"⚠️  Collection exists with wrong dimension ({current_dim} vs {self.embedding_dim})")
                print(f"🗑️  Deleting and recreating collection...")
                self.qdrant_client.delete_collection(self.collection_name)
                # Recreate with correct dimension
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
                )
                print(f"✅ Recreated collection: {self.collection_name} with dimension {self.embedding_dim}")
            else:
                print(f"✅ Collection exists: {self.collection_name} (dimension: {self.embedding_dim})")
        else:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
            print(f"✅ Created collection: {self.collection_name} (dimension: {self.embedding_dim})")

    def _read_markdown_files(self, base_dir: Path, refresh: bool = False) -> List[dict]:
        """Read all markdown files from the knowledge base directories.

        T048: Add document metadata tracking including source, title, file_path, and last_modified.
        T047: If refresh=True, only return files that have been modified since last ingestion.

        Args:
            base_dir: Base directory to search for markdown files
            refresh: If True, only return changed files (incremental update)

        Returns:
            List of document dicts with metadata
        """
        documents = []
        md_patterns = ["*.md", "README*"]

        # Define knowledge base directories
        kb_dirs = [
            base_dir / "specs",
            base_dir / ".specify",
            base_dir / "CLAUDE.md",
            base_dir / "README.md",
        ]

        # Track existing documents for incremental refresh (T047)
        existing_docs: Dict[str, dict] = {}
        if refresh:
            existing_docs = self._get_existing_documents()

        for kb_path in kb_dirs:
            if not kb_path.exists():
                continue

            if kb_path.is_file():
                files = [kb_path]
            else:
                files = []
                for pattern in md_patterns:
                    files.extend(kb_path.rglob(pattern))

            for file_path in files:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if not content.strip():
                        continue

                    # Get file metadata (T048)
                    file_stat = file_path.stat()
                    last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                    content_hash = hashlib.md5(content.encode()).hexdigest()

                    # For incremental refresh (T047), skip unchanged files
                    if refresh:
                        source_key = str(file_path.relative_to(base_dir))
                        if source_key in existing_docs:
                            existing_doc = existing_docs[source_key]
                            # Check if file has changed
                            if (existing_doc.get("content_hash") == content_hash and
                                existing_doc.get("last_modified") == last_modified.isoformat()):
                                continue  # Skip unchanged file

                    documents.append({
                        "source": str(file_path.relative_to(base_dir)),
                        "title": file_path.stem,
                        "content": content,
                        "file_path": str(file_path),
                        "last_modified": last_modified.isoformat(),  # T048: Track last modified time
                        "content_hash": content_hash,  # T047: Hash for change detection
                    })
                except Exception as e:
                    print(f"⚠️  Failed to read {file_path}: {e}")

        print(f"📚 Found {len(documents)} markdown documents" +
              (f" (incremental refresh)" if refresh else f" (full scan)"))
        return documents

    def _get_existing_documents(self) -> Dict[str, dict]:
        """Get existing documents from Qdrant for incremental refresh (T047).

        Returns:
            Dict mapping source -> document metadata
        """
        try:
            # Scroll through all points to extract source documents
            existing_docs: Dict[str, dict] = {}

            # Use scroll API to get all points
            results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Get all points
                with_payload=["source", "last_modified", "content_hash"],
            )[0]

            for point in results:
                source = point.payload.get("source", "")
                if source and source not in existing_docs:
                    # Store metadata from first chunk of each document
                    existing_docs[source] = {
                        "last_modified": point.payload.get("last_modified"),
                        "content_hash": point.payload.get("content_hash"),
                    }

            return existing_docs
        except Exception as e:
            print(f"⚠️  Failed to get existing documents: {e}")
            return {}

    def _delete_document_chunks(self, source: str):
        """Delete all chunks for a specific document (T047 refresh support).

        Args:
            source: Source file identifier
        """
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value=source),
                        )
                    ]
                ),
            )
        except Exception as e:
            print(f"⚠️  Failed to delete chunks for {source}: {e}")

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts using OpenRouter."""
        print(f"    🔢 Calling OpenRouter API for {len(texts)} chunks...")
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts,
            )
            print(f"    ✅ Got embeddings for {len(texts)} chunks")
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"    ❌ Embedding API error: {e}")
            raise

    def ingest(self, base_dir: Path, refresh: bool = False):
        """Main ingestion pipeline.

        T047: Support incremental refresh for changed files.
        T048: Store document metadata (last_modified, content_hash) with each chunk.

        Args:
            base_dir: Base directory containing documentation
            refresh: If True, only re-ingest modified documents (incremental update)
        """
        mode = "Incremental Refresh" if refresh else "Full Ingestion"
        print(f"\n{'='*60}")
        print(f"TeamFlow Knowledge Base {mode}")
        print(f"{'='*60}\n")

        # Setup collection
        self._setup_collection()

        # Read documents (with refresh logic if enabled)
        documents = self._read_markdown_files(base_dir, refresh=refresh)

        if not documents:
            print("ℹ️  No new or modified documents found.")
            return

        # Process documents
        all_points = []
        chunk_id = 0
        doc_count = 0
        deleted_count = 0

        print(f"\n🔄 Processing {len(documents)} documents...")

        for doc in documents:
            doc_count += 1
            print(f"\n[{doc_count}/{len(documents)}] 📄 {doc['title']}", end="")

            # For refresh mode, delete existing chunks first (T047)
            if refresh and doc.get("source"):
                self._delete_document_chunks(doc["source"])
                deleted_count += 1

            # Chunk document
            chunks = self.chunker.chunk_document(doc["content"])
            print(f" → {len(chunks)} chunks")

            # Generate embeddings for chunks
            embeddings = self._generate_embeddings(chunks)

            # Create points for Qdrant with metadata (T048)
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "source": doc["source"],
                        "title": doc["title"],
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        # T048: Add document metadata
                        "last_modified": doc.get("last_modified"),
                        "content_hash": doc.get("content_hash"),
                        "file_path": doc.get("file_path"),
                    },
                )
                all_points.append(point)
                chunk_id += 1

        # Batch upsert to Qdrant (in batches to avoid timeout)
        print(f"\n{'='*60}")
        print(f"💾 Storing {len(all_points)} chunks in Qdrant...")
        if refresh and deleted_count > 0:
            print(f"🗑️  Replaced {deleted_count} existing documents")
        print(f"{'='*60}")

        batch_size = 100  # Process in batches of 100 points
        total_batches = (len(all_points) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(all_points))
            batch = all_points[start_idx:end_idx]

            print(f"   Batch {batch_num + 1}/{total_batches} ({len(batch)} points)...", end="")
            try:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
                print(f" ✅")
            except Exception as e:
                print(f" ❌ Failed: {e}")
                # Continue with next batch instead of failing completely
                continue

        print(f"✅ All batches processed!")

        # Verify ingestion
        collection_info = self.qdrant_client.get_collection(self.collection_name)
        print(f"\n{'='*60}")
        print(f"✅ {mode} Complete!")
        print(f"{'='*60}")
        print(f"📊 Collection: {self.collection_name}")
        print(f"📦 Total vectors: {collection_info.points_count}")
        print(f"📐 Vector dimension: {collection_info.config.params.vectors.size}")
        print(f"{'='*60}\n")


def main(refresh: bool = False):
    """Run knowledge base ingestion.

    Args:
        refresh: If True, only re-ingest modified documents (T047)
    """
    # Get configuration - auto-detect base directory
    # Try multiple possible base locations for cross-platform compatibility
    possible_bases = [
        Path(__file__).parent.parent.parent.parent,  # From backend/app/jobs/ingest_knowledge_base.py -> repo root
        Path("D:/GIAIC/Quarter 4/Hackathon II"),  # Windows path
        Path("/mnt/d/GIAIC/Quarter 4/Hackathon II"),  # WSL/Linux path
    ]

    base_dir = None
    for path in possible_bases:
        if path.exists() and (path / "specs").exists():
            base_dir = path
            break

    if not base_dir:
        raise ValueError(
            f"Cannot find repository root. Searched: {[str(p) for p in possible_bases]}"
        )

    # Validate environment variables
    if not settings.qdrant_url or settings.qdrant_url == "your-qdrant-cloud-url-here":
        raise ValueError("QDRANT_URL not set in environment")

    if not settings.qdrant_api_key or settings.qdrant_api_key == "your-qdrant-api-key-here":
        raise ValueError("QDRANT_API_KEY not set in environment")

    if not settings.openrouter_api_key or settings.openrouter_api_key == "your-openrouter-api-key-here":
        raise ValueError("OPENROUTER_API_KEY not set in environment")

    # Create ingestor and run
    ingestor = KnowledgeBaseIngestor(
        qdrant_url=settings.qdrant_url,
        qdrant_api_key=settings.qdrant_api_key,
        openrouter_api_key=settings.openrouter_api_key,
    )

    ingestor.ingest(base_dir, refresh=refresh)


if __name__ == "__main__":
    main()
