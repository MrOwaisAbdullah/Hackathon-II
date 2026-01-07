# Production Lessons Learned - RAG Pipeline Builder

## Overview

This document captures critical lessons learned from implementing a production RAG system for TeamFlow CRM, covering real-world issues encountered and their solutions.

## Critical Issues Encountered

### 1. Wrong Embedding Model Selection

**Issue:** Used `mistralai/devstral-2512:free` which is a **chat model**, not an embedding model.

**Error:**
```
Error code: 400 - {'error': {'message': 'Model does not support embeddings output modality'}}
```

**Solution:**
- Use correct embedding model: `openai/text-embedding-3-small` (1536 dimensions)
- Verify model supports embeddings before implementation
- Use OpenRouter's filter: `?output_modalities=embeddings`

**Cost:** $0.02 per 1M tokens (~$0.008 for 778 chunks / ~400K tokens)

### 2. Memory Error in Chunking Loop

**Issue:** Infinite loop in `_split_text()` when `split_point - overlap <= current_position`

**Error:**
```
MemoryError: Cannot allocate memory
```

**Root Cause:**
```python
# BAD: Can create infinite loop
current_position = split_point - self.overlap
# When overlap >= split_point, position never advances
```

**Solution:**
```python
# GOOD: Always make progress
new_position = split_point - self.overlap
if new_position <= current_position:
    new_position = split_point  # Skip overlap if can't move back
current_position = new_position

# Also add safety limit
max_chunks = 10000
iterations = 0
while current_position < len(text) and iterations < max_chunks:
    iterations += 1
    # ... chunking logic ...
```

### 3. Code Block Duplication in Chunks

**Issue:** All placeholders replaced in ALL chunks, causing memory bloat

**Root Cause:**
```python
# BAD: Replaces all placeholders in every chunk
def _restore_code_blocks(self, text: str, placeholders: dict[str, str]) -> str:
    for placeholder, code_block in placeholders.items():
        text = text.replace(placeholder, code_block)  # Replaces everywhere!
    return text
```

**Solution:**
```python
# GOOD: Only replace if present, once per occurrence
def _restore_code_blocks(self, text: str, placeholders: dict[str, str]) -> str:
    result = text
    for placeholder, code_block in placeholders.items():
        if placeholder in result:  # Check if present
            result = result.replace(placeholder, code_block, 1)  # Replace once
    return result
```

### 4. Qdrant Upsert Timeout

**Issue:** Sending all 778 points in one batch times out

**Error:**
```
httpx.WriteTimeout: The write operation timed out
qdrant_client.http.exceptions.ResponseHandlingException
```

**Root Cause:**
```python
# BAD: Single large batch
self.qdrant_client.upsert(
    collection_name=self.collection_name,
    points=all_points,  # 778 points at once
)
```

**Solution:**
```python
# GOOD: Batch in groups of 100
batch_size = 100
total_batches = (len(all_points) + batch_size - 1) // batch_size

for batch_num in range(total_batches):
    start_idx = batch_num * batch_size
    end_idx = min(start_idx + batch_size, len(all_points))
    batch = all_points[start_idx:end_idx]

    self.qdrant_client.upsert(
        collection_name=self.collection_name,
        points=batch,
    )
```

### 5. Cross-Platform Path Detection

**Issue:** Hardcoded paths don't work across Windows, WSL, Linux

**Error:**
```
Found 0 markdown documents (using /mnt/d/... on Windows)
```

**Solution:**
```python
# Try multiple possible base locations
possible_bases = [
    Path(__file__).parent.parent.parent.parent,  # Relative path
    Path("D:/GIAIC/Quarter 4/Hackathon II"),     # Windows path
    Path("/mnt/d/GIAIC/Quarter 4/Hackathon II"), # WSL/Linux path
]

base_dir = None
for path in possible_bases:
    if path.exists() and (path / "specs").exists():
        base_dir = path
        break
```

### 6. Collection Dimension Mismatch

**Issue:** Existing collection has wrong dimension after model change

**Solution:**
```python
# Check dimension on startup
collection_info = self.qdrant_client.get_collection(self.collection_name)
current_dim = collection_info.config.params.vectors.size

if current_dim != self.embedding_dim:
    print(f"⚠️  Collection exists with wrong dimension ({current_dim} vs {self.embedding_dim})")
    print(f"🗑️  Deleting and recreating collection...")
    self.qdrant_client.delete_collection(self.collection_name)
    # Recreate with correct dimension
```

## OpenRouter Integration

### Why OpenRouter?

- **Unified API**: Access multiple AI providers with single API key
- **Cost Control**: Set spending limits, monitor usage
- **Model Flexibility**: Easy to switch between models
- **Free Tiers**: Access to free models for testing

### Implementation

```python
from openai import OpenAI

# Use OpenRouter as OpenAI-compatible endpoint
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

# Use OpenAI model via OpenRouter
response = client.embeddings.create(
    model="openai/text-embedding-3-small",
    input=chunk,
)
```

### Finding Free Embedding Models

**Warning:** As of January 2025, OpenRouter has **no free embedding models**. Free models are chat-only.

**To verify:**
```python
import urllib.request
import json

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
with urllib.request.urlopen(req) as response:
    models = json.loads(response.read().decode())

# Filter for embedding models
embedding_models = [
    m for m in models["data"]
    if "embeddings" in m.get("architecture", {}).get("output_modalities", [])
]
```

### Cost Calculation

```
Total chunks: 778
Avg tokens/chunk: ~500
Total tokens: 389,000 (~0.4M)

Cost: 0.4M × $0.02/1M = $0.008
```

## Embedding Model Reference

| Model | Dimensions | Cost | Context |
|-------|-----------|------|---------|
| `openai/text-embedding-3-small` | 1536 | $0.02/1M | 8,192 tokens |
| `openai/text-embedding-3-large` | 3072 | $0.13/1M | 8,192 tokens |
| `openai/text-embedding-ada-002` | 1536 | $0.10/1M | 8,191 tokens |

**Recommendation:** Use `text-embedding-3-small` for most cases. Best value for quality.

## Environment Configuration

### Required Variables

```bash
# .env
# AI Services
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
```

### Verification Script

```python
# test_openrouter.py
from openai import OpenAI

api_key = "sk-or-v1-..."
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

# Test embedding model
response = client.embeddings.create(
    model="openai/text-embedding-3-small",
    input=["Test sentence."],
)
print(f"✅ Dimension: {len(response.data[0].embedding)}")
```

## Chunking Best Practices

### Configuration

```python
chunk_size = 1000    # Characters (not tokens)
overlap = 200        # Overlap for context preservation
```

### Strategy

1. **Protect Code Blocks**: Never split code blocks
2. **Respect Structure**: Split at paragraphs → lines → sentences
3. **Prevent Loops**: Always advance position
4. **Limit Size**: Cap at 10,000 chunks per document

### Example Output

```
[1/37] 📄 data-model → 11 chunks
    🔢 Calling OpenRouter API for 11 chunks...
    ✅ Got embeddings for 11 chunks
```

## Qdrant Best Practices

### Connection

```python
from qdrant_client import QdrantClient

# Cloud
client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
)

# Local
client = QdrantClient(url="http://localhost:6333")
```

### Collection Setup

```python
from qdrant_client.models import VectorParams, Distance

client.create_collection(
    collection_name="teamflow_kb",
    vectors_config=VectorParams(
        size=1536,  # Match embedding dimension
        distance=Distance.COSINE,
    ),
)
```

### Batch Upsert Pattern

```python
batch_size = 100
for i in range(0, len(points), batch_size):
    batch = points[i:i + batch_size]
    client.upsert(collection_name=collection_name, points=batch)
```

### Search Pattern

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.search(
    collection_name="teamflow_kb",
    query_vector=embedding,
    limit=5,
    score_threshold=0.7,  # Cosine similarity threshold
)
```

## Troubleshooting Checklist

### Before Running Ingestion

- [ ] Verify API keys are set (check `.env`)
- [ ] Test embedding model with single request
- [ ] Confirm Qdrant cluster is accessible
- [ ] Check collection dimension matches embedding model
- [ ] Verify repository path is correct

### During Ingestion

- [ ] Watch for API errors (400, 401, 402, 429)
- [ ] Monitor memory usage
- [ ] Check batch processing logs
- [ ] Verify embeddings are generated

### After Ingestion

- [ ] Confirm point count in Qdrant
- [ ] Test semantic search with sample queries
- [ ] Verify relevance scores are acceptable
- [ ] Check chunk quality and size distribution

## Performance Metrics

### Ingestion Performance

```
Documents: 37 markdown files
Chunks: 778 total
Avg chunks/doc: 21

Embedding Generation:
- Time: ~2 minutes total
- Rate: ~13 chunks/second

Qdrant Upsert:
- Time: ~30 seconds (8 batches of 100)
- Rate: ~26 chunks/second

Total Cost: $0.008 (OpenRouter)
```

### Query Performance

```
Retrieval Latency: < 100ms for top 5 results
Generation Latency: ~1-2s (depending on model)
```

## Common Errors Summary

| Error | Cause | Fix |
|-------|-------|-----|
| `400 - does not support embeddings` | Wrong model (chat not embedding) | Use `openai/text-embedding-3-small` |
| `MemoryError` | Infinite loop in chunker | Add progress checks |
| `WriteTimeout` | Too many points in one batch | Batch in groups of 100 |
| `Found 0 documents` | Wrong path format | Try multiple path formats |
| `dimension mismatch` | Old collection, new model | Delete and recreate collection |

## Next Steps

1. **Add Caching**: Cache embeddings to avoid re-generation
2. **Incremental Updates**: Only process changed files
3. **Metadata Filtering**: Add filters for source, tags, dates
4. **Hybrid Search**: Combine semantic + keyword search
5. **Re-ranking**: Add re-ranking for better relevance

## Resources

- [OpenRouter Docs](https://openrouter.ai/docs)
- [Qdrant Python Client](https://python-client.qdrant.tech/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [text-embedding-3-small](https://openrouter.ai/openai/text-embedding-3-small)
