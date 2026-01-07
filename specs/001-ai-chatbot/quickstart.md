# Quickstart Guide: TeamFlow AI Chatbot (Phase 3)

**Feature**: 001-ai-chatbot | **Branch**: `001-ai-chatbot` | **Date**: 2025-01-06

---

## Overview

This guide provides step-by-step instructions for setting up and running the Phase 3 AI Chatbot locally.

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| uv | Latest | Python package manager |
| npm | Latest | Node.js package manager |
| Docker | Latest | Qdrant vector DB (optional) |

### Required Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Qdrant** | `https://your-cluster.cloud.qdrant.io` | Vector store for RAG (Cloud) |
| **Gemini API** | `generativelanguage.googleapis.com` | AI model |
| **OpenAI API** | `api.openai.com` | Embeddings for RAG |

---

## 1. Environment Setup

### 1.1 Clone Repository

```bash
git clone <repository-url>
cd teamflow-web
git checkout 001-ai-chatbot
```

### 1.2 Backend Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/teamflow

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# AI Services
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key  # For embeddings only

# Qdrant (Cloud)
# Get free cluster at https://cloud.qdrant.io/
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# App Settings
ENV=development
LOG_LEVEL=debug
```

### 1.3 Frontend Environment Variables

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## 2. Backend Setup

### 2.1 Install Dependencies

```bash
cd backend
uv sync
```

### 2.2 Run Database Migrations

```bash
uv run alembic upgrade head
```

### 2.3 Setup Qdrant Cloud

1. Create a free Qdrant Cloud cluster at https://cloud.qdrant.io/
2. Copy your cluster URL and API key
3. Update `.env` with your credentials (see 2.1 above)

### 2.4 Ingest Knowledge Base

```bash
# Ingest project docs into Qdrant
uv run python -m app.jobs.ingest_knowledge_base
```

**Expected Output**:
```
Ingesting constitution.md... 12 chunks
Ingesting spec.md... 25 chunks
Ingesting TEAMFLOW-PLAN.md... 40 chunks
✅ Ingested 77 chunks to Qdrant
```

### 2.5 Start Backend Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open `http://localhost:8000/docs` for API docs.

---

## 3. Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Start Development Server

```bash
npm run dev
```

**Verify**: Open `http://localhost:3000`

---

## 4. Testing the Chatbot

### 4.1 Access Chat Widget

1. Login to TeamFlow (use Better Auth)
2. Chat widget appears in bottom-right corner
3. Click to open

### 4.2 Test Natural Language Commands

**English**:
```
You: Create a high priority task to fix the navbar for the Acme project
Bot: I'll create that task. Task "Fix navbar" created with priority HIGH for Acme project.
```

**Urdu**:
```
You: Acme project ke liye navbar fix ka task banayein
Bot: Main woh task bana raha hoon. "Fix navbar" task Acme project ke liye ban gaya hai.
```

### 4.3 Test Voice Input

1. Click microphone icon in chat input
2. Speak command (e.g., "Show my tasks")
3. Transcript appears in input field
4. Send message

---

## 5. MCP Tools Testing

### 5.1 List Available Tools

```bash
# Test MCP server directly
uv run python -m app.mcp.test_tools
```

**Expected Output**:
```
Available MCP Tools:
- add_task: Create a new task
- list_tasks: List tasks with filters
- assign_task: Assign task to user
- complete_task: Mark task as complete
- get_profitability: Get project profitability
- workload_summary: Get team workload
- suggest_assignee: Suggest best assignee
```

### 5.2 Test Tool Execution

```bash
# Test add_task tool
curl -X POST http://localhost:8000/api/v1/chat/respond \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "'$CONV_ID'",
    "message": "Create a task to test the MCP integration"
  }'
```

---

## 6. Troubleshooting

### 6.1 "AI Service Unavailable"

**Symptom**: Chat responds with "AI features unavailable" error.

**Solution**:
1. Check `GEMINI_API_KEY` is set correctly
2. Verify Gemini API quota not exceeded
3. Check backend logs: `tail -f backend/logs/app.log`

---

### 6.2 "Knowledge Base Empty"

**Symptom**: RAG queries return no results.

**Solution**:
1. Verify Qdrant Cloud connection: Check your cluster URL and API key in `.env`
2. Re-run ingestion: `uv run python -m app.jobs.ingest_knowledge_base`
3. Check embeddings: OpenAI API key required

---

### 6.3 "Chat Token Invalid"

**Symptom**: 401 Unauthorized on chat requests.

**Solution**:
1. Verify Better Auth session is active
2. Check token expiration (7-day limit)
3. Re-login to refresh session

---

### 6.4 Voice Input Not Working

**Symptom**: Microphone button doesn't respond.

**Solution**:
1. Check browser support (Chrome recommended)
2. Verify microphone permissions granted
3. Check console for errors: F12 → Console tab

---

## 7. Development Workflow

### 7.1 Run Tests

```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm run test
```

### 7.2 Type Checking

```bash
# Backend (mypy)
cd backend
uv run mypy app/

# Frontend (tsc)
cd frontend
npm run type-check
```

### 7.3 Linting

```bash
# Backend (pylint)
cd backend
uv run pylint app/

# Frontend (eslint)
cd frontend
npm run lint
```

---

## 8. Production Deployment

### 8.1 Backend (HuggingFace Spaces)

```bash
# Build and push
cd backend
uv run docker build -t teamflow-backend .
docker push teamflow-backend
```

### 8.2 Frontend (Vercel)

```bash
# Deploy
cd frontend
npm run build
vercel --prod
```

---

## 9. Skills & Agents Reference

During implementation, use these specialized skills:

| Skill | Purpose | Command |
|-------|---------|---------|
| `openai-chatkit-integration` | ChatKit backend/frontend | Use via Skill tool |
| `openai-agents-sdk-gemini` | Agent orchestration | Use via Skill tool |
| `mcp-builder` | MCP server best practices | Use via Skill tool |
| `rag-pipeline-builder` | Qdrant ingestion | Use via Skill tool |

### MCP Servers for Development

| MCP Server | Purpose |
|------------|---------|
| `context7` | Fetch latest docs |
| `web-search` | Research patterns |
| `chrome-devtools` | Debug frontend |
| `zai-mcp-server` | UI screenshots |

---

## 10. Next Steps

1. **Implement Backend**: Follow MCP tool definitions in `contracts/chat-api.yaml`
2. **Implement Frontend**: Integrate `@openai/chatkit-react` widget
3. **Add Voice**: Implement `useVoiceInput` hook
4. **Test E2E**: Verify chat flow with Playwright
5. **Deploy**: Push to HuggingFace (backend) and Vercel (frontend)

---

## Support

- **Issues**: Create GitHub issue
- **Docs**: See `/specs/001-ai-chatbot/` for detailed specs
- **Constitution**: See `.specify/memory/constitution.md` for principles

---

**Status**: ✅ Complete

Quickstart guide ready for development setup.
