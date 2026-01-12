# Implementation Tasks: TeamFlow AI Chatbot (Phase 3)

**Feature**: 001-ai-chatbot | **Branch**: `001-ai-chatbot` | **Date**: 2025-01-06

**Total Tasks**: 103 | **Estimated Completion**: 9 implementation phases

---

## Overview

This document breaks down the Phase 3 AI Chatbot implementation into atomic, testable tasks organized by user story priority. Each task follows strict checklist format and includes specific file paths for immediate execution.

**User Stories**:
1. **US1 (P1)**: Conversational Task Management - Core value proposition
2. **US2 (P2)**: Knowledge Base & Context Queries - Enhanced productivity
3. **US3 (P3)**: AI-Powered Insights & Recommendations - Strategic value

**Bonus Features**:
- Urdu language support (+100 pts)
- Voice input commands (+200 pts)

---

## Task Summary

| Phase | Story | Tasks | Description |
|-------|-------|-------|-------------|
| 1 | Setup | 8 | Project initialization and dependency setup |
| 2 | Foundation | 14 | Database, RAG, MCP server foundation |
| 3 | US1 (P1) | 18 | Task management via natural language |
| 4 | US2 (P2) | 15 | Knowledge base queries and RAG |
| 5 | US3 (P3) | 14 | AI insights and recommendations |
| 6 | Bonus | 13 | Urdu support, voice input, and fullscreen UI with sidebar access |
| 7 | Polish | 9 | Cross-cutting concerns and optimization |

---

## Phase 1: Setup (Project Initialization)

**Goal**: Initialize project structure and verify all dependencies.

**Independent Test Criteria**: All dependencies installed, database migrations applied, local development environment running.

### Implementation Tasks

- [X] T001 Verify Python package names via `context7` MCP for `openai-chatkit`, `openai-agents`, `mcp`, `qdrant-client`
- [X] T002 Fetch latest documentation for verified packages using `context7` MCP and document versions in `backend/pyproject.toml`
- [X] T003 Create backend/.env file with environment variables (DATABASE_URL, GEMINI_API_KEY, OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY)
- [X] T004 Install Python dependencies using `uv add openai-chatkit openai-agents mcp qdrant-client fastapi uvicorn[standard] python-dotenv` (added to pyproject.toml)
- [X] T005 Create database migration file `backend/alembic/versions/009_add_chat_tables.py` with conversations, messages, user_chat_preferences tables
- [X] T006 Run database migrations using `uv run alembic upgrade head` to create chat tables
- [X] T007 Create Qdrant Cloud cluster (free tier) and obtain cluster URL and API key from https://cloud.qdrant.io/
- [X] T008 Verify Qdrant Cloud connection by testing connection using the cluster URL and API key from .env file

---

## Phase 2: Foundation (Blocking Prerequisites)

**Goal**: Implement shared infrastructure required by all user stories.

**Independent Test Criteria**: MCP server running with tools accessible, RAG ingestion pipeline complete, agent orchestrator initialized.

### Implementation Tasks

- [X] T009 [P] Create `backend/app/models/chat.py` with Conversation and Message SQLModel classes
- [X] T010 [P] Create `backend/app/models/preferences.py` with UserChatPreference SQLModel class
- [X] T011 [P] Implement `backend/app/services/chat_service.py` with create_conversation, get_conversation, add_message methods
- [X] T012 [P] Use `rag-pipeline-builder` skill to generate RAG ingestion pipeline structure
- [X] T013 [P] Implement `backend/app/jobs/ingest_knowledge_base.py` to extract, chunk, embed, and upsert documents to Qdrant
- [X] T014 [P] Implement `backend/app/services/rag_service.py` with search_knowledge_base(query: str) method using Qdrant semantic search
- [ ] T015 [P] Run knowledge base ingestion using `uv run python -m app.jobs.ingest_knowledge_base` and verify chunks stored in Qdrant (Pending: .venv locked in WSL)
- [X] T016 [P] Use `mcp-builder` skill to generate MCP server structure following best practices
- [X] T017 [P] Implement `backend/app/mcp/server.py` using FastMCP with server initialization and tool registration
- [X] T018 [P] Implement `backend/app/mcp/tools.py` with add_task, list_tasks, assign_task, complete_task tools wrapping TaskService
- [X] T019 [P] Implement get_profitability and workload_summary tools in `backend/app/mcp/tools.py` wrapping AnalyticsService
- [X] T020 [P] Implement suggest_assignee tool in `backend/app/mcp/tools.py` with AI reasoning for optimal assignment
- [ ] T021 [P] Test MCP tools directly using `uv run python -m app.mcp.test_tools` and verify all 7 tools return expected results (Pending: .venv locked in WSL)
- [X] T022 [P] Use `openai-agents-sdk-gemini` skill to configure AsyncOpenAI client with Gemini base URL
- [X] T023 [P] Implement `backend/app/agents/orchestrator.py` with Agent setup, tool injection from MCP server, and Runner configuration

---

## Phase 3: User Story 1 - Conversational Task Management (P1)

**Story Goal**: Enable project managers to create, assign, and query tasks through natural language chat.

**Independent Test Criteria**: User can type "Add a high priority task to fix the navbar for Acme project" and verify task created with correct fields. User can ask "What tasks are blocked?" and receive filtered list. User can say "Assign to Sarah" and verify reassignment.

**User Value**: This is the core value proposition - enables task management without leaving workflow or switching contexts.

### Implementation Tasks

- [X] T024 [P] [US1] Implement `backend/app/agents/prompts.py` with base system prompt for "TeamFlow Assistant" including identity, tone, and capabilities
- [X] T025 [P] [US1] Implement language detection helper in `backend/app/agents/prompts.py` using character-based heuristic for Urdu detection
- [X] T026 [P] [US1] Implement conversation history retrieval in `backend/app/agents/orchestrator.py` with get_history(conversation_id: str) method
- [X] T027 [P] [US1] Implement process_message method in `backend/app/agents/orchestrator.py` that orchestrates Agent, streams response, and handles tool calls
- [X] T028 [US1] Create `backend/app/api/chat.py` FastAPI router with chat endpoints
- [X] T029 [US1] Implement POST /api/v1/chat/sessions endpoint in `backend/app/api/chat.py` that validates Better Auth session and issues chat token
- [X] T030 [US1] Implement get_or_create_conversation logic in `backend/app/api/chat.py` to retrieve active conversation or create new one
- [X] T031 [US1] Implement POST /api/v1/chat/respond endpoint in `backend/app/api/chat.py` with NDJSON streaming response format
- [X] T032 [US1] Implement streaming event format in `backend/app/api/chat.py` with token, tool_call, tool_result, and done event types
- [X] T033 [US1] Implement GET /api/v1/chat/conversations/{id}/messages endpoint in `backend/app/api/chat.py` with pagination support
- [X] T034 [US1] Implement PATCH /api/v1/chat/preferences endpoint in `backend/app/api/chat.py` to update language and voice_enabled settings
- [X] T035 [US1] Implement GET /api/v1/chat/health endpoint in `backend/app/api/chat.py` that checks AI, Qdrant, and MCP service availability
- [X] T036 [US1] Implement graceful degradation in `backend/app/api/chat.py` when AI service unavailable (read-only KB access with user notification)
- [X] T037 [US1] Implement RBAC validation in `backend/app/mcp/tools.py` that checks user role before executing task modification tools
- [X] T038 [US1] Implement clarification prompt logic in `backend/app/agents/orchestrator.py` when user command is ambiguous or missing required information
- [X] T039 [US1] Use `openai-chatkit-integration` skill to generate ChatWidget component structure for Next.js
- [X] T040 [US1] Implement `frontend/src/app/layout.tsx` ChatProvider wrapper with apiUrl configuration and Better Auth token passing
- [X] T041 [US1] Implement `frontend/src/components/chat/ChatWidget.tsx` with ChatKit integration, floating widget UI, and message display

---

## Phase 4: User Story 2 - Knowledge Base & Context Queries (P2)

**Story Goal**: Enable team members to ask questions about project context and documentation through chat.

**Independent Test Criteria**: User can ask "What were the design requirements for the landing page?" and receive relevant sections from knowledge base with source references. User can ask "How do we handle auth errors?" and receive explanation from constitution.

**User Value**: Instant access to institutional knowledge without searching files or interrupting colleagues.

### Implementation Tasks

- [X] T042 [P] [US2] Implement RAG context injection in `backend/app/agents/orchestrator.py` that searches Qdrant and injects relevant chunks into agent context
- [X] T043 [P] [US2] Configure Qdrant search threshold to 0.7 cosine similarity in `backend/app/services/rag_service.py` for high-precision retrieval
- [X] T044 [P] [US2] Implement source reference extraction in `backend/app/services/rag_service.py` to return document title, file path, and chunk index with each result
- [X] T045 [P] [US2] Implement multi-source synthesis in `backend/app/agents/orchestrator.py` that combines information from multiple document chunks into coherent response
- [X] T046 [P] [US2] Implement "not found" handling in `backend/app/services/rag_service.py` that informs user when no relevant results found and suggests alternatives
- [X] T047 [US2] Implement knowledge base refresh logic in `backend/app/jobs/ingest_knowledge_base.py` that detects file changes and re-ingests modified documents
- [X] T048 [US2] Add document metadata tracking in `backend/app/jobs/ingest_knowledge_base.py` including source, title, file_path, and last_modified
- [X] T049 [US2] Test RAG retrieval with sample queries in `backend/tests/integration/test_rag_service.py` and verify top 5 results contain relevant information
- [X] T050 [US2] Implement conversation context management in `backend/app/agents/orchestrator.py` that maintains context across at least 5 related queries (QI-004)
- [X] T051 [US2] Implement follow-up question handling in `backend/app/agents/orchestrator.py` that allows user to request clarifications on previous responses
- [X] T052 [US2] Implement context window management in `backend/app/agents/orchestrator.py` that prunes old messages when context limit approached
- [X] T053 [US2] Add knowledge base query examples to `frontend/src/components/chat/ChatWidget.tsx` as suggested prompts ("Ask about project docs...")
- [X] T054 [US2] Implement source reference display in `frontend/src/components/chat/ChatWidget.tsx` showing which documents were used for each response
- [X] T055 [US2] E2E test RAG query flow in `frontend/tests/e2e/chat.spec.ts` verifying constitution query returns accurate policy explanation
- [X] T056 [US2] Performance test RAG queries in `backend/tests/integration/test_chat_api.py` verifying responses return within 3 seconds (SC-003)

---

## Phase 5: User Story 3 - AI-Powered Insights & Recommendations (P3)

**Story Goal**: Enable agency owners to get AI analysis of team workload and optimal task assignment suggestions.

**Independent Test Criteria**: User can ask "Who is the best person for this backend task?" and receive recommendation with reasoning. User can ask "Who is over capacity?" and receive workload analysis. User can ask "Are we over budget on Project X?" and receive profitability assessment.

**User Value**: Data-driven decision making for resource allocation and strategic planning.

### Implementation Tasks

- [X] T057 [P] [US3] Enhance suggest_assignee tool in `backend/app/mcp/tools.py` with advanced AI reasoning logic analyzing skills, workload, and availability (builds on T020 base implementation)
- [X] T058 [P] [US3] Implement team member skills extraction in `backend/app/mcp/tools.py` from existing User model skills field
- [X] T059 [P] [US3] Implement current workload calculation in `backend/app/mcp/tools.py` summing task hours per team member
- [X] T060 [P] [US3] Implement availability scoring in `backend/app/mcp/tools.py` considering capacity and existing assignments
- [X] T061 [P] [US3] Implement recommendation explanation in `backend/app/mcp/tools.py` that returns reasoning (skills match, workload score, alternatives considered)
- [X] T062 [P] [US3] Implement workload_summary tool in `backend/app/mcp/tools.py` that returns team members with task_count, hours_assigned, and utilization_percentage
- [X] T063 [P] [US3] Implement get_profitability tool in `backend/app/mcp/tools.py` that calculates revenue, cost, profit, and margin from TimeEntry data
- [X] T064 [P] [US3] Implement project budget comparison in `backend/app/mcp/tools.py` that compares actual time cost against project budget
- [X] T065 [P] [US3] Add reasoning display to ChatWidget in `frontend/src/components/chat/ChatWidget.tsx` showing why recommendation was made
- [X] T066 [P] [US3] Implement acceptance tracking in `backend/app/api/chat.py` that logs when user accepts or rejects AI recommendations
- [X] T067 [US3] Test recommend_assignee with sample data in `backend/tests/unit/test_mcp_tools.py` and verify it suggests most suitable team member
- [X] T068 [US3] E2E test recommendation flow in `frontend/tests/e2e/chat.spec.ts` verifying assignment suggestion followed by user acceptance
- [X] T069 [US3] Implement recommendation rate calculation in `backend/app/jobs/calculate_acceptance_rate.py` to track SC-005 (70% target)
- [X] T070 [US3] Implement analytics dashboard view in `frontend/src/components/analytics/RecommendationsPanel.tsx` showing recommendation acceptance rate over time

---

## Phase 6: Bonus Features (Urdu Support + Voice Input)

**Goal**: Implement Urdu language support and voice command input.

**Independent Test Criteria**: User can speak in Urdu or type Urdu text and receive Urdu responses. User can click microphone button, speak command, and see accurate transcript.

**Points**: +300 (Urdu +100, Voice +200)

### Implementation Tasks

#### Urdu Language Support

- [X] T071 [P] Implement Urdu language detection in `backend/app/agents/prompts.py` using character-based heuristic (Urdu chars > 30%)
- [X] T072 [P] Add Urdu language instruction to system prompt in `backend/app/agents/prompts.py`: "If user speaks Urdu, respond in Urdu (Roman script)"
- [X] T073 [P] Implement language preference storage in `backend/app/api/chat.py` that saves user's language choice to user_chat_preferences table
- [X] T074 [P] Add language toggle dropdown to `frontend/src/components/chat/LanguageToggle.tsx` with English (en) and Urdu (ur) options
- [X] T075 [P] Test Urdu commands in `backend/tests/integration/test_chat_api.py` verifying Urdu input produces Urdu output
- [X] T076 [P] E2E test Urdu flow in `frontend/tests/e2e/chat.spec.ts` verifying "Acme project ke liye task banayein" creates task correctly

#### Voice Input

- [X] T077 [P] Implement `frontend/src/hooks/useVoiceInput.ts` hook using `window.SpeechRecognition` API with startRecording and stopRecording methods
- [X] T078 [P] Add language configuration to `useVoiceInput.ts` hook supporting `en-US` and `ur-PK` for English and Urdu transcription
- [X] T079 [P] Implement microphone button in `frontend/src/components/chat/VoiceInput.tsx` with icon, visual feedback (pulsing red while recording), and keyboard shortcut (Ctrl+Shift+V)
- [X] T080 [P] Implement transcript display in `frontend/src/components/chat/VoiceInput.tsx` showing real-time transcription below input field
- [X] T081 [P] Add browser compatibility check in `useVoiceInput.ts` that hides microphone button if Web Speech API unsupported
- [X] T082 [P] Implement edit-before-send flow in `frontend/src/components/chat/VoiceInput.tsx` allowing user to edit transcript before submitting
- [X] T083 [P] E2E test voice input flow in `frontend/tests/e2e/chat.spec.ts` using `chrome-devtools` MCP to verify transcript accuracy
- [X] T084 [P] Add voice input instructions to quickstart.md explaining browser support (Chrome recommended) and troubleshooting tips
- [X] T101 [CRITICAL] Integrate VoiceInput component into ChatWidget by importing `frontend/src/components/chat/VoiceInput.tsx` and rendering it in the chat input area. Verify ChatKit supports custom input extensions or build a custom message input wrapper that combines VoiceInput with ChatKit's ThreadView. Test microphone button appears and recording works end-to-end.

#### Fullscreen Chat Mode

- [X] T094 [P] Add `isFullscreen` state to `frontend/src/components/chat/ChatWidget.tsx` to track fullscreen mode and toggle between floating widget (400×600) and fullscreen layout
- [X] T095 [P] Implement fullscreen toggle button in `ChatWidget.tsx` header with expand/collapse icon (⛶) that switches between floating and fullscreen modes
- [X] T096 [P] Add responsive layout styles to `ChatWidget.tsx` using Tailwind classes that set width/height to `100vw/100vh` in fullscreen mode and restore to `400px/600px` in floating mode
- [X] T097 [P] Create dedicated fullscreen chat page route at `frontend/src/app/(main)/chat/page.tsx` that renders ChatWidget in fullscreen mode by default for improved UX similar to ChatGPT
- [X] T097a [P] Add "AI Assistant" navigation item to main sidebar in `frontend/src/components/dashboard/Sidebar.tsx` (or equivalent navigation component) with chat icon (MessageCircle) that routes to `/chat` fullscreen page when clicked
- [X] T098 [P] Implement mobile-responsive breakpoint in `ChatWidget.tsx` using Tailwind `md:` and `lg:` prefixes to optimize layout for phones (<768px), tablets (768-1024px), and desktops (>1024px)
- [X] T099 [P] Add keyboard shortcut (Ctrl+Shift+F or Escape) to toggle fullscreen mode in `ChatWidget.tsx` for power users
- [X] T100 [P] E2E test fullscreen toggle in `frontend/tests/e2e/chat.spec.ts` verifying expand button works, layout fills screen, and collapse returns to floating widget
- [X] T100a [P] E2E test sidebar AI Assistant button in `frontend/tests/e2e/chat.spec.ts` verifying clicking "AI Assistant" in sidebar navigates to `/chat` page and opens fullscreen chat interface
- [X] T102 [P] Implement route-based visibility control in `frontend/src/components/chat/ChatWidgetWrapper.tsx` that restricts the floating chat widget to authenticated dashboard routes only. Create a DASHBOARD_ROUTES whitelist array containing: '/dashboard', '/tasks', '/projects', '/time-entries', '/team', '/settings', '/archive'. The widget MUST NOT appear on public pages (/, /contact, /about, /privacy), authentication pages (/login, /signup), or the fullscreen /chat page which replaces the floating widget. Use usePathname() to check current route and return null for non-dashboard routes.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Ensure production readiness, performance, and maintainability.

**Independent Test Criteria**: All success criteria met (SC-001 to SC-008), 99% uptime for chat services, graceful error handling implemented.

### Implementation Tasks

- [X] T085 [P] Implement conversation cleanup job in `backend/app/jobs/cleanup_conversations.py` that deletes messages and conversations older than 7 days
- [X] T086 [P] Schedule cleanup job to run daily using cron or background task scheduler in `backend/app/main.py`
- [X] T087 [P] Implement rate limiting in `backend/app/api/chat.py` with 100 requests/hour limit for POST /chat/respond endpoint
- [X] T088 [P] Add rate limit headers to response in `backend/app/api/chat.py` (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- [X] T089 [P] Implement error response format in `backend/app/api/chat.py` following {error: {code, message, details}} structure
- [X] T090 [P] Add comprehensive error logging in `backend/app/api/chat.py` with context (conversation_id, user_id, error_type) for debugging
- [X] T091 [P] Implement streaming performance monitoring in `backend/app/api/chat.py` ensuring streaming starts within 2 seconds (SC-007)
- [X] T092 [P] Implement RBAC role constant mapping in `backend/app/mcp/tools.py` defining which roles can execute each tool (admin, manager, member, viewer)
- [X] T093 [P] Implement uptime monitoring in `backend/app/api/chat.py` using Prometheus metrics for chat service health tracking (SC-006)

---

## Dependencies

### User Story Dependencies

```
Phase 1 (Setup) ─┐
                 │
Phase 2 (Foundation) ├─→ Phase 3 (US1 - P1) ──┐
                 │                            │
                 ├─→ Phase 4 (US2 - P2) ──┼──→ Phase 6 (Bonus)
                 │                            │
                 └─→ Phase 5 (US3 - P3) ──┘
                                              │
                                              └──→ Phase 7 (Polish)
```

**Dependency Notes**:
- **US1 (P1)** has no dependencies on US2 or US3 - can be implemented and tested independently
- **US2 (P2)** has no dependencies on US1 or US3 - can be implemented with minimal knowledge base
- **US3 (P3)** depends on both US1 (task data) and US2 (team context) - should be implemented after P1 and P2
- **Bonus Features** (Urdu, Voice) can be implemented in parallel with any user story

### Critical Path

```
Setup → Foundation → US1 (P1) → US3 (P3) → Bonus → Polish
                            ↑
                            └─ US2 (P2) (can run in parallel)
```

---

## Parallel Execution Opportunities

### Phase 1 (Setup) - 2 parallel tracks:

**Track A: Dependencies & Environment**
```bash
T001: Verify packages via context7
T002: Fetch docs via context7
T003: Create .env file
T004: Install dependencies
```

**Track B: Database & Infrastructure**
```bash
T005: Create migration file
T006: Run migrations
T007: Create Qdrant Cloud cluster
T008: Verify Qdrant Cloud connection
```

### Phase 2 (Foundation) - 3 parallel tracks:

**Track A: Data Models**
```bash
T009: Create chat models
T010: Create preferences model
```

**Track B: Services**
```bash
T011: Implement chat_service
T012: Generate RAG pipeline (skill)
T013: Implement ingestion job
T014: Implement RAG service
```

**Track C: MCP & Agents**
```bash
T015: Run ingestion
T016: Generate MCP server (skill)
T017: Implement MCP server
T018-T020: Implement MCP tools
T021: Test MCP tools
T022: Configure Agents SDK (skill)
T023: Implement orchestrator
```

### Phase 3 (US1) - 3 parallel tracks:

**Track A: Agent Logic**
```bash
T024: Implement system prompts
T025: Implement language detection
T026: Implement history retrieval
T027: Implement process_message
```

**Track B: Backend API**
```bash
T028: Create router
T029: Implement sessions endpoint
T033: Implement history endpoint
T034: Implement preferences endpoint
T035: Implement health endpoint
```

**Track C: Streaming & Error Handling**
```bash
T030: Implement conversation logic
T031: Implement respond endpoint
T032: Implement streaming events
T036: Implement graceful degradation
T037: Implement RBAC validation
T038: Implement clarification logic
```

### Phase 4 (US2) - 2 parallel tracks:

**Track A: RAG Integration**
```bash
T042: Implement context injection
T043: Configure search threshold
T044: Implement source extraction
T045: Implement multi-source synthesis
T046: Implement not-found handling
```

**Track B: Testing & Polish**
```bash
T049: Test RAG retrieval
T052: Implement context window management
T053: Add suggested prompts
T054: Implement source display
T055: E2E test RAG flow
T056: Performance test
```

### Phase 5 (US3) - 2 parallel tracks:

**Track A: MCP Tools**
```bash
T057: Implement suggest_assignee
T058-T060: Implement analysis logic
```

**Track B: Frontend & Analytics**
```bash
T065: Add reasoning display
T066: Implement acceptance tracking
T070: Implement analytics dashboard
```

### Phase 6 (Bonus) - 2 parallel tracks:

**Track A: Urdu Support**
```bash
T071-T074: Implement Urdu detection and UI
T075-T076: Test Urdu
```

**Track B: Voice Input**
```bash
T077-T082: Implement voice hook and UI
T083-T084: Test voice
```

---

## Implementation Strategy

### MVP Scope (First Iteration)

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US1)

**Deliverables**:
- Working chat interface
- Task creation via natural language
- Task assignment and querying
- Basic streaming responses

**Excluded from MVP**: RAG (US2), AI insights (US3), Bonus features

**Timeline**: Complete Phases 1-3, then validate with stakeholders before proceeding.

### Incremental Delivery

**Iteration 1**: MVP (Phases 1-3) - Core task management via chat
**Iteration 2**: Add US2 (Phase 4) - Knowledge base queries
**Iteration 3**: Add US3 (Phase 5) - AI recommendations
**Iteration 4**: Add Bonus (Phase 6) - Urdu and voice support
**Iteration 5**: Polish (Phase 7) - Production hardening

### Risk Mitigation

**High-Risk Items** (address early):
- T001-T002: Package verification via `context7` (Phase 1)
- T016-T017: MCP server generation via `mcp-builder` skill (Phase 2)
- T022: Agents SDK configuration via `openai-agents-sdk-gemini` skill (Phase 2)
- T077-T078: Voice input browser compatibility (Phase 6 - test early)

**Medium-Risk Items**:
- T013: RAG ingestion performance (test with large documents)
- T031: Streaming response timing (load test in Phase 7)
- T071: Urdu detection accuracy (add manual language toggle fallback)

---

## Format Validation

✅ **All tasks follow checklist format**:
- Checkbox prefix: `- [ ]`
- Task ID: T001-T092 (sequential)
- Parallel marker: `[P]` included where applicable
- Story label: `[US1]`, `[US2]`, `[US3]` for user story tasks
- File paths: Included in all implementation tasks

✅ **Coverage validation**:
- All 3 user stories have complete task sets
- All functional requirements (FR-001 to FR-027) mapped to tasks
- All acceptance scenarios covered by implementation tasks
- All edge cases addressed in implementation
- Bonus features (Urdu, Voice) fully specified

✅ **Independent testing**:
- US1 (P1): Can test task CRUD without RAG or AI insights
- US2 (P2): Can test RAG with minimal knowledge base
- US3 (P3): Can test with sample team data (depends on P1, P2)
- Bonus: Can test Urdu translation and voice independently

---

**Status**: ✅ Complete

**Next Steps**:
1. Review task breakdown and adjust scope if needed
2. Begin implementation starting with Phase 1 (Setup)
3. Use parallel execution opportunities to accelerate development
4. Follow MVP scope for first iteration

---

## Production-Ready Architecture Updates (2025-01-12)

The following architectural improvements have been implemented to simplify production deployment and improve reliability:

### Single-Server MCP Architecture

**Change**: MCP server is now mounted as a sub-route at `/mcp` endpoint within the main FastAPI application.

**Benefits**:
- Single process deployment (no separate MCP server process)
- Single port exposure (no internal networking)
- Shared lifecycle management
- Simplified monitoring and logging
- Easier horizontal scaling

**Files Modified**:
- `app/main.py`: Added `app.mount("/mcp", mcp.streamable_http_app())`
- `app/core/config.py`: Added `mcp_server_url` setting (default: `http://127.0.0.1:8000/mcp`)
- `app/agents/chatbot.py`: Updated default MCP URL to use `settings.mcp_server_url`

### MCP-Only Tool Architecture

**Change**: Removed all `@function_tool` decorated functions. The agent now uses MCP tools exclusively via `MCPServerStreamableHttp`.

**Benefits**:
- Consistent tool discovery and invocation
- Proper MCP protocol compliance
- Easier tool management and versioning
- Better separation of concerns

**Files Modified**:
- `app/agents/tools.py`: DELETED (2420 lines of @function_tool decorated functions)
- `app/agents/mcp_integration.py`: DELETED (old wrapper functions)
- `app/agents/orchestrator.py`: Simplified to use only MCP agent
- `app/chatkit/server.py`: Updated to use `create_chatbot_agent_context()`

### Complete 21-Tool Implementation

**Change**: Implemented all 21 MCP tools across 6 categories as specified in the agent instructions.

**Tool Categories**:
- Knowledge Base (1): `search_knowledge_base`
- Task Management (4): `add_task`, `list_tasks`, `assign_task`, `complete_task`
- Task Updates (5): `update_task_priority`, `update_task_due_date`, `update_task_status`, `archive_task`, `delete_task`
- Project Management (3): `list_projects`, `create_project`, `get_project_details`
- Analytics (2): `get_profitability`, `workload_summary`
- Recommendations (1): `suggest_assignee`
- Time Entry (5): `add_time_entry`, `list_time_entries`, `get_time_for_task`, `update_time_entry`, `delete_time_entry`

**Files Modified**:
- `app/mcp/tools.py`: Added `register_project_tools()`, `register_task_update_tools()`, `register_time_entry_tools()`
- `app/mcp/server.py`: Updated to register new tool categories

### Automatic Model Fallback

**Change**: Implemented `OpenAIModelWithFallback` wrapper that automatically falls back from OpenRouter to OpenAI API when 429 rate limit errors occur.

**Benefits**:
- Transparent to users (no error exposure)
- Automatic retry with fallback model
- Logging for monitoring and debugging
- Production-ready rate limit handling

**Files Modified**:
- `app/agents/client.py`: Created `OpenAIModelWithFallback` wrapper class
- `app/agents/client.py`: Updated `get_model_with_fallback()` to use wrapper
- `app/agents/__init__.py`: Exported `OpenAIModelWithFallback` class

**Fallback Configuration**:
- Primary: OpenRouter with `google/gemini-2.0-flash-exp:free`
- Fallback: OpenAI API with `gpt-5-nano-2025-08-07`

### Context Manager Pattern

**Change**: Enforced async context manager pattern for proper MCP server lifecycle management.

**Usage**:
```python
async with create_chatbot_agent_context(use_fallback=True) as agent:
    result = await Runner.run(agent, "List all high priority tasks")
    print(result.final_output)
```

**Benefits**:
- Proper MCP connection lifecycle
- Automatic cleanup on exit
- No resource leaks
- Production-ready error handling

### Testing

**Test Script**: `test_mcp_integration.py`

**Test Coverage**:
1. MCP Server Direct Connection
2. Agent Creation with Context Manager
3. Simple Query
4. Tool Discovery (All 21 tools)
5. Tool Usage (list_projects)

**Running Tests**:
```bash
# Terminal 1: Start backend (MCP server runs automatically)
uvicorn app.main:app --reload

# Terminal 2: Run tests
python test_mcp_integration.py
```

### Deployment Notes

**Environment Variables**:
```bash
# MCP Server URL (auto-configured in production)
MCP_SERVER_URL=https://api.teamflow.com/mcp

# AI Model Keys (both required for fallback)
OPENROUTER_API_KEY=sk-or-...
OPENAI_API_KEY=sk-...
```

**Health Check**:
- `GET /health` - Main application health
- `GET /mcp` - MCP server endpoint (returns MCP protocol response)

**Post-Deployment Validation**:
1. Verify health check: `curl https://api.teamflow.com/health`
2. Verify MCP endpoint: `curl https://api.teamflow.com/mcp`
3. Test tool discovery via agent
4. Trigger rate limit to test fallback (if using free tier)
