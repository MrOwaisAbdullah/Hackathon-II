---
name: openai-chatkit-integration
description: Implement OpenAI ChatKit with a custom advanced backend using Python (FastAPI), Qdrant for RAG, and OpenAI Agents SDK pointing to alternative LLMs (Gemini/OpenRouter). Use when building full-stack chat applications that require custom retrieval logic or non-OpenAI models while keeping the ChatKit UI. Supports uv package manager.
---

# OpenAI ChatKit Integration (Custom Backend)

## Overview

This skill guides you through implementing a custom backend for OpenAI ChatKit, bypassing OpenAI's hosted services to use alternative LLMs and custom RAG pipelines.

It leverages patterns from:
- **`rag-pipeline-builder`**: For robust document chunking, embedding, and Qdrant storage.
- **`openai-agents-sdk-gemini`**: For using the Agents SDK with non-OpenAI models, including guardrails and advanced tool usage.

## Required Clarifications

Before generating code, ask:
1.  **LLM Provider**: "Which LLM provider will you use? (Gemini, OpenRouter, Local/Ollama?)"
2.  **Vector DB**: "Do you have a Qdrant Cloud URL/Key, or should we set up a local Docker instance?"
3.  **Frontend Framework**: "Are you using Next.js (App Router or Pages Router) or pure React?"

## Pre-flight Checklist

### Must Have
- [ ] **API Keys**: Gemini/OpenRouter Key, Qdrant Key, and OpenAI Key (for embeddings only).
- [ ] **Python Env**: `uv` installed for dependency management.
- [ ] **Node Env**: `@openai/chatkit-react` installed.

### Must Avoid
- [ ] **clientSecret**: Do NOT use `clientSecret` in frontend; use custom `api.url`.
- [ ] **OpenAI Keys**: Do NOT use OpenAI-hosted features (like Assistants API) with non-OpenAI models.

## Workflow

1.  **Backend Setup**: Initialize with `uv` and `pyproject.toml`.
2.  **RAG Configuration**: Index documents using the intelligent chunking ingestion script.
3.  **Agent Logic**: Configure the Agents SDK with a custom `base_url` and guardrails.
4.  **Frontend Connection**: Point ChatKit JS to the FastAPI `/chatkit` endpoint.

## 1. Backend Implementation

The backend uses `uv` for performance and modern standards.

### Dependency Management
Use `assets/backend/pyproject.toml`.
```bash
uv sync
```

### Server Code
Use the template in `assets/backend/server.py`. This template implements:
- **Custom ChatKitServer**: Handles protocol details.
- **Guardrails**: Uses `openai-agents-sdk-gemini` patterns for input safety.
- **RAG Integration**: Connects to Qdrant for context retrieval.

## 2. RAG & Knowledge Base

1.  **Utilities**: `assets/backend/scripts/rag_utils.py` provides intelligent chunking and embedding logic (derived from `rag-pipeline-builder`).
2.  **Ingestion**: Run `assets/backend/scripts/ingest.py` to index your data.
    ```bash
    python assets/backend/scripts/ingest.py --collection my_docs
    ```
3.  **Retrieval**: See `references/rag-setup.md` for integration details.

## 3. Frontend Implementation

Use the template in `assets/frontend/ChatPage.tsx`. Ensure the `api.url` matches your FastAPI server's address.

## Reference Material

| Resource | Description |
|----------|-------------|
| `references/architecture.md` | Data flow and component overview |
| `references/rag-setup.md` | Detailed RAG implementation guide |
| `references/chatkit-protocol.md` | NDJSON event types and API endpoints |
| `references/advanced-agent.md` | Structured output, tools, and handoffs |

## Assets

| Asset | Path |
|-------|------|
| Backend Template | `assets/backend/server.py` |
| Pyproject Configuration | `assets/backend/pyproject.toml` |
| RAG Utilities | `assets/backend/scripts/rag_utils.py` |
| Ingestion Script | `assets/backend/scripts/ingest.py` |
| Frontend Component | `assets/frontend/ChatPage.tsx` |

## Official Documentation

| Resource | URL |
|----------|-----|
| ChatKit Guide | https://platform.openai.com/docs/guides/chatkit |
| Custom Backend | https://platform.openai.com/docs/guides/custom-chatkit |
| Gemini API | https://ai.google.dev/gemini-api/docs/openai |

## Troubleshooting

- **CORS**: Ensure FastAPI middleware allows your frontend URL.
- **NDJSON**: Ensure `media_type="application/x-ndjson"` is set in `StreamingResponse`.
- **Agents Client**: Always use `set_default_openai_client` when using non-OpenAI models.
- **Embeddings**: Ensure the embedding dimension in Qdrant (1536 for text-embedding-3-small) matches your model.
