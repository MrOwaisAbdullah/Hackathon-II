# Implementation Plan: TeamFlow AI Chatbot (Phase 3)

**Branch**: `001-ai-chatbot` | **Date**: 2025-01-06 | **Spec**: [spec.md](./spec.md)

---

## Summary

Transform the TeamFlow CRM into an intelligent agentic system with a conversational interface. Users can create tasks, assign work, query profitability, and access project knowledge through natural language (English and Urdu) with optional voice input.

**Technical Approach**: Custom FastAPI backend using OpenAI ChatKit (Python) + OpenAI Agents SDK with Gemini 2.0 + Official MCP SDK (FastMCP) for tool exposure + Qdrant for RAG knowledge retrieval.

---

## Technical Context

**Language/Version**: Python 3.13+, TypeScript 5+, Node.js 20+

**Primary Dependencies**:
- Backend: `fastapi`, `openai-chatkit`, `openai-agents`, `mcp` (FastMCP), `qdrant-client`, `sqlmodel`
- Frontend: `next@16`, `@openai/chatkit-react`, `framer-motion`

**Storage**: Neon PostgreSQL (existing), Qdrant (new for RAG)

**Testing**: `pytest`, `vitest`, `playwright`

**Target Platform**: Linux server (Vercel + HuggingFace Spaces)

**Project Type**: Web (full-stack with custom backend)

**Performance Goals**:
- Chat streaming starts within 2 seconds (95th percentile)
- Knowledge base queries return within 3 seconds (95th percentile)
- API endpoints under 200ms (95th percentile)

**Constraints**:
- Must use custom FastAPI backend (not OpenAI hosted ChatKit)
- Must integrate with existing Better Auth sessions
- Must support English and Urdu languages
- 7-day conversation retention

**Scale/Scope**:
- 3 new database tables (conversations, messages, preferences)
- 7 MCP tools wrapping existing services
- 1 Qdrant collection with ~100 document chunks
- 2 bonus features: Urdu support, voice input

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Compliance Verification

- [x] **Existing agents/skills consulted first**: Used `openai-chatkit-integration`, `openai-agents-sdk-gemini`, `mcp-builder`, `rag-pipeline-builder` skills
- [x] **SOLID principles followed**: Service layer maintains SRP; MCP tools use protocols (DIP); agent orchestrator injects tools (OCP)
- [x] **DRY applied**: Shared utilities in `/backend/shared/`; chat widget composable component
- [x] **Tests written first (TDD)**: Unit tests for MCP tools, integration tests for API, E2E for chat flows
- [x] **Type safety enforced**: Pydantic for all inputs, TypeScript strict mode
- [x] **Security standards met**: Better Auth session validation, RBAC on all tools, input validation
- [x] **Performance targets defined**: 2s streaming start, 3s KB queries, 200ms API p95
- [x] **MCP tools considered**: Official MCP SDK used, tools designed per `mcp-builder` best practices

**Status**: ✅ All gates passed. No violations to justify.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation blueprint)
├── research.md          # Phase 0 research (complete)
├── data-model.md        # Phase 1 data model (complete)
├── quickstart.md        # Phase 1 quickstart (complete)
├── contracts/           # Phase 1 API contracts (complete)
│   └── chat-api.yaml    # OpenAPI specification
└── tasks.md             # To be created by /sp.tasks
```

### Source Code (repository root)

```text
teamflow-web/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   └── migrations/
│   │   │       └── 003_add_chat_tables.sql
│   │   ├── models/
│   │   │   ├── chat.py           # Conversation, Message models
│   │   │   └── preferences.py     # UserChatPreference model
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       └── chat.py        # ChatKit server endpoints
│   │   ├── api/endpoints/
│   │   │   └── chatkit.py         # ChatKit integration
│   │   ├── services/
│   │   │   ├── rag_service.py     # Qdrant integration
│   │   │   ├── chat_service.py    # Conversation & message management
│   │   │   └── ...
│   │   ├── mcp/
│   │   │   ├── server.py          # FastMCP server (mounted at /mcp)
│   │   │   └── tools.py           # 21 MCP tool implementations
│   │   ├── agents/
│   │   │   ├── client.py          # OpenAI/OpenRouter client + fallback
│   │   │   ├── chatbot.py         # Agent context manager
│   │   │   └── orchestrator.py    # Agent + Runner setup
│   │   ├── core/
│   │   │   └── config.py          # MCP_SERVER_URL configuration
│   │   ├── main.py                # Single FastAPI app with /mcp mount
│   │   └── jobs/
│   │       ├── ingest_knowledge_base.py  # RAG ingestion
│   │       └── cleanup_conversations.py  # 7-day retention
│   └── tests/
│       ├── unit/
│       │   ├── test_mcp_tools.py
│       │   └── test_agents.py
│       ├── integration/
│       │   └── test_mcp_streamablehttp.py
│       └── test_mcp_integration.py  # Manual test script
│
└── frontend/
    └── src/
        ├── app/
        │   └── layout.tsx          # ChatProvider wrapper
        ├── components/
        │   └── chat/
        │       ├── ChatWidget.tsx  # Floating chat widget
        │       └── ChatHeader.tsx  # Language toggle, voice button
        └── hooks/
            └── useVoiceInput.ts    # Web Speech API hook
```

**Architecture Notes:**
- MCP server is mounted in `app/main.py` at `/mcp` endpoint
- Agent uses `MCPServerStreamableHttp` for tool integration
- `OpenAIModelWithFallback` wrapper handles 429 rate limit errors
- `create_chatbot_agent_context()` provides proper async context management

**Structure Decision**: Option 2 (Web application) with backend/frontend separation. Extends existing Phase II structure with new chat-focused modules.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js 16)                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  ChatWidget (@openai/chatkit-react)                                   │ │
│  │  - Floating widget or sidebar                                          │ │
│  │  - Message list with streaming NDJSON                                  │ │
│  │  - Input with voice button (useVoiceInput hook)                       │ │
│  │  - Language toggle (English/Urdu)                                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ SSE / HTTP POST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              BACKEND - Single FastAPI Process (Port 8000)                  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Main API Endpoints (/api/v1/*)                                        │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐ │ │
│  │  │  POST /chat/sessions  →  Validate Better Auth, issue token        │ │ │
│  │  │  POST /chat/respond    →  Orchestrate Agent, stream response      │ │ │
│  │  └────────────────────────────────────────────────────────────────────┘ │ │
│  │                              │                                          │ │
│  │                              ▼                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Agent Orchestrator (OpenAI Agents SDK)                            │ │ │
│  │  │  - System prompt (multi-language, role context)                    │ │ │
│  │  │  - Agent + Runner setup with OpenRouter + OpenAI fallback         │ │ │
│  │  │  - Context manager pattern for proper MCP lifecycle               │ │ │
│  │  │  - Automatic 429 rate limit fallback                              │ │ │
│  │  │  - Conversation history retrieval                                  │ │ │
│  │  └────────────────────────────────────────────────────────────────────┘ │ │
│  │                              │                                          │ │
│  │                              ▼                                          │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐ │ │
│  │  │  MCP Server (Mounted at /mcp) - FastMCP                            │ │ │
│  │  │  Knowledge Base: search_knowledge_base                             │ │ │
│  │  │  Task Management: add_task, list_tasks, assign_task, complete_task│ │ │
│  │  │  Task Updates: update_task_priority, update_task_due_date,         │ │ │
│  │  │                update_task_status, archive_task, delete_task      │ │ │
│  │  │  Project Management: list_projects, create_project,               │ │ │
│  │  │                     get_project_details                            │ │ │
│  │  │  Analytics: get_profitability, workload_summary                    │ │ │
│  │  │  Recommendations: suggest_assignee                                 │ │ │
│  │  │  Time Entry: add_time_entry, list_time_entries, get_time_for_task,│ │ │
│  │  │              update_time_entry, delete_time_entry                  │ │ │
│  │  │  Total: 21 tools exposed via MCPServerStreamableHttp              │ │ │
│  │  └────────────────────────────────────────────────────────────────────┘ │ │
│  │                              │                                          │ │
│  │            ┌─────────────────┴──────────────────┐                     │ │
│  │            ▼                                    ▼                     │ │
│  │  ┌──────────────────────┐          ┌─────────────────────┐           │ │
│  │  │  Service Layer       │          │  Qdrant (RAG)       │           │ │
│  │  │  (Phase II)          │          │  - Constitution     │           │ │
│  │  │  TaskService         │          │  - Specs            │           │ │
│  │  │  ProjectService      │          │  - Project Plan     │           │ │
│  │  │  AnalyticsService    │          │  - Semantic Search  │           │ │
│  │  └──────────────────────┘          └─────────────────────┘           │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
│  ┌──────────────────────┐          ┌─────────────────────┐                  │
│  │  Neon PostgreSQL      │          │  AI Models           │                  │
│  │  - users, tasks       │          │  (Primary)           │                  │
│  │  - conversations      │          │  OpenRouter:         │                  │
│  │  - messages           │          │  google/gemini-2.0   │                  │
│  │  - preferences        │          │  -flash-exp:free     │                  │
│  └──────────────────────┘          │  (Fallback)          │                  │
│                                   │  OpenAI API:         │                  │
│                                   │  gpt-5-nano-2025-08- │                  │
│                                   │  07                  │                  │
│                                   └─────────────────────┘                  │
│                                                                              │
│  ┌──────────────────────┐                                                   │
│  │  OpenAI Embeddings    │                                                   │
│  │  text-embedding-3-    │                                                   │
│  │  small               │                                                   │
│  └──────────────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Production-Ready Deployment Architecture

**Single Process, Single Port:**

The backend implements a unified deployment architecture where both the main FastAPI application and the MCP server run in a single process. The MCP server is mounted as a sub-route at `/mcp` endpoint.

**Benefits:**
- Single container/VM deployment
- No internal networking complexity
- Shared lifecycle management
- Simplified monitoring and logging
- Easier horizontal scaling

**Configuration:**
```bash
# Development (default)
MCP_SERVER_URL=http://127.0.0.1:8000/mcp

# Production (override via environment variable)
MCP_SERVER_URL=https://api.teamflow.com/mcp
```

---

## Implementation Steps

### Phase 1: Foundation (Setup & Verification)

**Step 1.1**: Verify Package Names via `context7` MCP
- Use `mcp__context7__resolve-library-id` for: `openai-chatkit`, `openai-agents`, `mcp`
- Fetch latest docs and confirm compatible versions
- Document versions in `research.md`

**Step 1.2**: Install Dependencies
```bash
cd backend
uv add openai-chatkit openai-agents mcp qdrant-client
uv add fastapi uvicorn[standard] python-dotenv
```

**Step 1.3**: Create Database Migration
- File: `backend/app/db/migrations/003_add_chat_tables.sql`
- Tables: `conversations`, `messages`, `user_chat_preferences`
- Run: `uv run alembic upgrade head`

---

### Phase 2: RAG Pipeline (Knowledge Base)

**Step 2.1**: Use `rag-pipeline-builder` Skill
- Skill location: `.claude/skills/rag-pipeline-builder/`
- Generate ingestion pipeline script

**Step 2.2**: Implement Ingestion Job
- File: `backend/app/jobs/ingest_knowledge_base.py`
- Extract: Read `.specify/memory/constitution.md`, `specs/001-ai-chatbot/spec.md`, `TEAMFLOW-PLAN.md`
- Chunk: Split into 500-1000 char chunks with overlap
- Embed: Use OpenAI `text-embedding-3-small`
- Upsert: Store in Qdrant `teamflow_kb` collection

**Step 2.3**: Implement RAG Service
- File: `backend/app/services/rag_service.py`
- Methods: `search_knowledge_base(query: str) -> List[DocumentChunk]`
- Use semantic search with 0.7 score threshold

---

### Phase 3: MCP Server (Tool Layer)

**Step 3.1**: Use `mcp-builder` Skill
- Skill location: `.claude/skills/mcp-builder/`
- Follow MCP best practices guide

**Step 3.2**: Implement MCP Server
- File: `backend/app/mcp/server.py`
- Use `FastMCP` from `mcp.server.fastmcp` for decorators and Pydantic integration
- Mount in `app/main.py` at `/mcp` endpoint using `app.mount("/mcp", mcp.streamable_http_app())`
- No separate process needed - runs in same FastAPI application

**Step 3.3**: Implement MCP Tools (21 tools total)
- File: `backend/app/mcp/tools.py`
- Organize into separate register functions per category:
  - `register_knowledge_base_tools()`: `search_knowledge_base` (1 tool)
  - `register_task_tools()`: `add_task`, `list_tasks`, `assign_task`, `complete_task` (4 tools)
  - `register_task_update_tools()`: `update_task_priority`, `update_task_due_date`, `update_task_status`, `archive_task`, `delete_task` (5 tools)
  - `register_project_tools()`: `list_projects`, `create_project`, `get_project_details` (3 tools)
  - `register_analytics_tools()`: `get_profitability`, `workload_summary` (2 tools)
  - `register_recommendation_tools()`: `suggest_assignee` (1 tool)
  - `register_time_entry_tools()`: `add_time_entry`, `list_time_entries`, `get_time_for_task`, `update_time_entry`, `delete_time_entry` (5 tools)

**Step 3.4**: Wrap Existing Services
- All tools call existing Phase II services (`TaskService`, `ProjectService`, `AnalyticsService`)
- Maintain SRP: tools handle validation, services handle logic

---

### Phase 4: Agent Orchestrator (AI Brain)

**Step 4.1**: Use `openai-agents-sdk-gemini` Skill
- Skill location: `.claude/skills/openai-agents-sdk-gemini/`
- Configure AsyncOpenAI client for Gemini compatibility

**Step 4.2**: Implement Agent Context Manager
- File: `backend/app/agents/chatbot.py`
- Use `MCPServerStreamableHttp` from OpenAI Agents SDK
- Implement `create_chatbot_agent_context()` as async context manager
- Proper lifecycle: MCP connection on enter, cleanup on exit
- MCP server URL: Use `settings.mcp_server_url` (default: `http://127.0.0.1:8000/mcp`)

**Step 4.3**: Implement Model Fallback
- File: `backend/app/agents/client.py`
- Create `OpenAIModelWithFallback` wrapper class
- Intercept `complete()` and `stream_complete()` API calls
- Detect 429 rate limit errors from OpenRouter
- Automatically retry with OpenAI `gpt-5-nano-2025-08-07`
- Log fallback actions for monitoring

**Step 4.4**: Define System Prompts
- File: `backend/app/agents/chatbot.py`
- Base prompt: "You are TeamFlow AI, an intelligent assistant for agency project management..."
- Multi-language: "If user speaks Urdu, respond in Urdu (Roman script)"
- RBAC: "Only admins/managers can assign tasks. Members can only view their own."
- All 21 tools documented in prompt for agent awareness

---

### Phase 5: Backend API (ChatKit Server)

**Step 5.1**: Use `openai-chatkit-integration` Skill
- Skill location: `.claude/skills/openai-chatkit-integration/`
- Generate ChatKit server structure

**Step 5.2**: Implement Chat Endpoints
- File: `backend/app/api/chat.py`
- `POST /api/v1/chat/sessions`: Validate Better Auth, issue chat token, get/create conversation
- `POST /api/v1/chat/respond`: Process message, orchestrate agent, stream NDJSON response
- `GET /api/v1/chat/conversations/{id}/messages`: Retrieve conversation history
- `PATCH /api/v1/chat/preferences`: Update user language/voice settings
- `GET /api/v1/chat/health`: Service health check

**Step 5.3**: Implement Streaming
- Use NDJSON format: `{"type": "token", "content": "..."}`
- Events: `token`, `tool_call`, `tool_result`, `done`
- Ensure streaming starts within 2 seconds (SC-007)

---

### Phase 6: Frontend Integration (ChatKit UI)

**Step 6.1**: Use `openai-chatkit-integration` Skill
- Generate ChatWidget component with streaming support

**Step 6.2**: Integrate ChatProvider
- File: `frontend/src/app/layout.tsx`
- Wrap with `<ChatProvider apiUrl="/api/v1/chat">`
- Pass Better Auth session token

**Step 6.3**: Implement ChatWidget
- File: `frontend/src/components/chat/ChatWidget.tsx`
- Use `@openai/chatkit-react` hooks
- Floating widget or sidebar panel
- Theme: Inherit "Eco-Modern" (lime/black) from Phase 2

**Step 6.4**: Implement Language Toggle
- Dropdown in chat header
- Options: English, Urdu
- Updates `user_chat_preferences.language`

---

### Phase 7: Voice Input (Bonus Feature)

**Step 7.1**: Implement `useVoiceInput` Hook
- File: `frontend/src/hooks/useVoiceInput.ts`
- Use `window.SpeechRecognition` API
- Language detection: `en-US` or `ur-PK`

**Step 7.2**: Add Voice Button
- Microphone icon in chat input area
- Visual feedback: Pulsing red while recording
- Keyboard shortcut: `Ctrl+Shift+V`

**Step 7.3**: Integrate with ChatWidget
- Transcript populates input field
- User can edit before sending
- Fallback: Hide button if API unsupported

---

### Phase 8: Testing & Validation

**Step 8.1**: Unit Tests
- MCP tools: Mock services, test input/output
- Agent logic: Mock tool calls, test prompts
- Language detection: Test edge cases

**Step 8.2**: Integration Tests
- Chat API endpoints with `httpx.AsyncClient`
- RAG retrieval (query → Qdrant → results)
- MCP tool execution

**Step 8.3**: E2E Tests
- Playwright for critical journeys:
  1. "Create task via chat" → Verify in DB
  2. "Assign to Sarah" → Verify assignee updated
  3. "How do we handle auth errors?" → Verify RAG response
  4. Urdu input → Urdu output
  5. Voice command → Transcript accuracy

**Step 8.4**: Browser Testing
- Use `chrome-devtools` MCP to verify:
  - WebSocket/SSE streaming works
  - ChatWidget renders correctly (theme match)
  - Voice input functional (Chrome)

---

### Phase 9: Deployment

**Step 9.1**: Backend (Single-Server Architecture)
- Dockerfile with Python 3.13
- **Important**: MCP server is mounted at `/mcp` endpoint - no separate process needed
- Environment variables:
  ```bash
  OPENROUTER_API_KEY=sk-or-...
  OPENAI_API_KEY=sk-...  # For fallback
  MCP_SERVER_URL=https://api.teamflow.com/mcp
  QDRANT_URL=https://your-qdrant-cloud-url
  QDRANT_API_KEY=...
  ```
- Qdrant URL (use Qdrant Cloud or external)
- Single process deployment: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Step 9.2**: Frontend (Vercel)
- Next.js build with static export
- Environment variables for API URL
- Deploy to production

**Step 9.3**: Post-Deployment
- Run health check: `GET /health`
- Verify MCP endpoint: `curl https://api.teamflow.com/mcp` (should return MCP protocol response)
- Ingest knowledge base to production Qdrant
- Monitor logs for errors
- Test fallback mechanism by triggering rate limit (if using free tier)

---

## Skills & Agents Usage Summary

| Phase | Skill/Agent | Purpose |
|-------|-------------|---------|
| 1 | `context7` MCP | Verify package names and versions |
| 2 | `rag-pipeline-builder` | Build Qdrant ingestion pipeline |
| 3 | `mcp-builder` | Implement MCP server with best practices |
| 4 | `openai-agents-sdk-gemini` | Configure Agent with Gemini |
| 5 | `openai-chatkit-integration` | Build ChatKit server and frontend |
| 6 | `openai-chatkit-integration` | Integrate ChatWidget UI |
| 7 | `web-search` MCP | Research Web Speech API patterns |
| 8 | `chrome-devtools` MCP | Debug streaming and UI |
| 8 | `zai-mcp-server` MCP | Verify chat widget styling |

---

## Success Criteria Validation

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| SC-001 | Create task in < 30s | E2E test with timing |
| SC-002 | 90% command accuracy | Test suite with NL commands |
| SC-003 | KB queries < 3s | Integration test with Qdrant |
| SC-004 | 50% time reduction | User survey (post-launch) |
| SC-005 | 70% recommendation acceptance | Track acceptance rate |
| SC-006 | 99% uptime (excl AI) | Monitoring (Prometheus) |
| SC-007 | Streaming starts in 2s | Load test with streaming |
| SC-008 | Multi-step chat workflows | E2E test scenarios |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenRouter API rate limits (429) | Low | **Automatic fallback** to OpenAI API via `OpenAIModelWithFallback` wrapper - transparent to users |
| OpenAI API unavailable | Medium | Graceful degradation with informative error message |
| Qdrant downtime | Medium | Cache embeddings locally |
| Web Speech API unsupported | Low | Graceful degradation (typing only) |
| Urdu detection accuracy | Low | Add manual language toggle |
| 7-day retention cleanup | Low | Scheduled cron job |
| MCP server scale issues | Low | Single-server architecture scales with main backend - no separate process management |

---

## Next Steps

1. **Verify this plan** against specification and constitution
2. **Run `/sp.tasks`** to break down into atomic implementation steps
3. **Begin implementation** following Phase 1-9 order
4. **Create ADRs** for significant architectural decisions if needed

---

**Status**: ✅ Complete

Implementation blueprint ready for task breakdown.
