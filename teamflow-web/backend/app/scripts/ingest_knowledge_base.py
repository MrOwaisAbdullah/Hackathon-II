"""Knowledge base ingestion script (G3 - Specification Analysis Finding).

Ingests documentation into Qdrant knowledge base for RAG queries.
Processes markdown files from the project and indexes them for semantic search.

Usage:
    python -m app.scripts.ingest_knowledge_base

Requirements:
    - Qdrant connection configured (QDRANT_URL, QDRANT_API_KEY)
    - Embeddings API configured (OPENROUTER_API_KEY)
"""
import asyncio
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from app.services.rag_service import rag_service


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# File patterns to include/exclude
INCLUDE_PATTERNS = [
    "*.md",          # Markdown files
    "README*",       # README files
    "*.mdx",         # MDX files (React markdown)
]

EXCLUDE_PATTERNS = [
    "node_modules/*",
    ".next/*",
    ".venv/*",
    "__pycache__/*",
    "*.pyc",
    ".git/*",
    "dist/*",
    "build/*",
    ".env*",
]


def find_document_files(root_path: Path) -> List[Path]:
    """Find all documentation files in the project.

    Args:
        root_path: Root directory to search

    Returns:
        List of file paths to ingest
    """
    files = []

    for pattern in INCLUDE_PATTERNS:
        # Use rglob for recursive search
        for file_path in root_path.rglob(pattern):
            # Check if file should be excluded
            if any(file_path.match(excl) for excl in EXCLUDE_PATTERNS):
                continue

            # Check if file exists and is readable
            if file_path.is_file():
                files.append(file_path)

    # Remove duplicates and sort
    files = sorted(set(files))
    return files


def extract_file_metadata(file_path: Path, root_path: Path) -> Dict:
    """Extract metadata from file path for indexing.

    Args:
        file_path: Path to the file
        root_path: Root directory for relative path calculation

    Returns:
        Metadata dictionary
    """
    relative_path = file_path.relative_to(root_path)

    # Determine document type from path
    doc_type = "documentation"
    if "spec" in str(relative_path):
        doc_type = "specification"
    elif "task" in str(relative_path):
        doc_type = "task"
    elif "README" in file_path.name:
        doc_type = "readme"
    elif "test" in str(relative_path):
        doc_type = "test"

    return {
        "source": str(relative_path),
        "title": file_path.stem,
        "type": doc_type,
        "extension": file_path.suffix,
        "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
    }


async def ingest_file(file_path: Path, root_path: Path) -> bool:
    """Ingest a single file into the knowledge base.

    Args:
        file_path: Path to the file to ingest
        root_path: Root directory for metadata

    Returns:
        True if successful, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        # Skip if empty or too small
        if len(content.strip()) < 50:
            logger.debug(f"Skipping {file_path} (too small: {len(content)} chars)")
            return False

        # Extract metadata
        metadata = extract_file_metadata(file_path, root_path)

        # Add first line as description if available
        lines = content.strip().split("\n")
        if lines:
            first_line = lines[0].strip("# ").strip()
            if len(first_line) > 10 and len(first_line) < 200:
                metadata["description"] = first_line

        # Index the document
        await rag_service.index_document(
            content=content,
            metadata=metadata,
        )

        logger.info(f"Ingested: {metadata['source']} ({len(content)} chars)")
        return True

    except Exception as e:
        logger.error(f"Failed to ingest {file_path}: {e}")
        return False


async def main():
    """Main ingestion routine (G3 - Specification Analysis Finding)."""
    logger.info("=" * 60)
    logger.info("TeamFlow Knowledge Base Ingestion")
    logger.info("=" * 60)

    # Get root path (project root)
    root_path = Path(__file__).parent.parent.parent.parent
    logger.info(f"Root path: {root_path}")

    # Find all documentation files
    logger.info("Scanning for documentation files...")
    files = find_document_files(root_path)
    logger.info(f"Found {len(files)} documentation files")

    if not files:
        logger.warning("No files found to ingest!")
        return

    # Ingest files
    logger.info("Starting ingestion...")
    ingested = 0
    failed = 0
    skipped = 0

    # Process in batches to avoid overwhelming the service
    batch_size = 10
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1}/{(len(files) + batch_size - 1) // batch_size}")

        for file_path in batch:
            success = await ingest_file(file_path, root_path)
            if success:
                ingested += 1
            else:
                skipped += 1

    # Summary
    logger.info("=" * 60)
    logger.info("Ingestion Complete")
    logger.info(f"  Successfully ingested: {ingested}")
    logger.info(f"  Skipped: {skipped}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total files: {len(files)}")
    logger.info("=" * 60)

    # Test search
    logger.info("Testing knowledge base search...")
    try:
        results = await rag_service.search_knowledge_base(
            query="TeamFlow AI chatbot",
            limit=3
        )
        logger.info(f"Search test returned {len(results)} results")
        for result in results[:2]:
            logger.info(f"  - {result.get('metadata', {}).get('title', 'Unknown')}")
    except Exception as e:
        logger.warning(f"Search test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
