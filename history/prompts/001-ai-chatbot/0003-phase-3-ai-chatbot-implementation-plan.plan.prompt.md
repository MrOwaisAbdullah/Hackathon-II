---
id: 0003
title: Phase 3 AI Chatbot Implementation Plan
stage: plan
date: 2025-01-06
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: MrOwaisAbdullah
command: /sp.plan
labels: ["plan", "phase3", "ai-chatbot", "rag", "openai-chatkit", "agents-sdk", "mcp", "voice", "urdu"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot/plan.md (created - complete implementation blueprint)
  - specs/001-ai-chatbot/research.md (created - technical research and decisions)
  - specs/001-ai-chatbot/data-model.md (created - data model and schema)
  - specs/001-ai-chatbot/quickstart.md (created - development setup guide)
  - specs/001-ai-chatbot/contracts/chat-api.yaml (created - API contracts)
  - specs/001-ai-chatbot/contracts/ (created - contracts directory)
tests:
  - Constitution check: PASSED (all 8 gates verified)
  - Research phase: Complete (all technical unknowns resolved)
  - Data model: Complete (3 new tables, Qdrant collection defined)
  - API contracts: Complete (5 endpoints, streaming NDJSON, error codes)
  - Architecture: Complete (9 implementation phases, skill mappings)
---

## Prompt

# Phase 3: TeamFlow AI Chatbot Implementation Plan Prompt

You are acting as the **Chief AI Architect** for TeamFlow. Your goal is to generate the **Technical Implementation Plan** (`sp.plan`) for Phase 3 of the project based on the requirements defined in the specification and the project plan.

## Context
We are executing **Phase 3: AI-Powered Task Chatbot** of the TeamFlow Agency CRM.
This phase transforms the CRM into an intelligent agentic system.

**Key Requirements (from @TEAMFLOW-PLAN.md):**
*   **Integrated AI Chatbot:** Implement a conversational interface using **OpenAI Chatkit**, **OpenAI Agents SDK**, and the **Official MCP SDK**.
*   **Custom Backend:** Use FastAPI + `openai-chatkit` (Python) + `openai-agents` (Python) instead of OpenAI's hosted services.
*   **Intelligence:** Google Gemini 2.0 (via OpenAI Compat) + Qdrant Vector DB.
*   **Official MCP SDK:** The tools must be exposed via an MCP Server built with the official `mcp` Python SDK (FastMCP).

**Bonus Features (Mandatory for this Plan):**
1.  **Multi-language Support (Urdu)** (+100 pts): The chatbot must understand and respond in Urdu.
2.  **Voice Commands** (+200 pts): Add voice input for todo commands using the Web Speech API.

## Directive
Run the `sp.plan` process to generate the architecture plan file (`specs/phase3-plan.md`).

**CRITICAL SKILL USAGE:**
The plan MUST explicitly mandate the use of the following skills for each component:
1.  **`openai-chatkit-integration`**: For the core ChatKit backend/frontend setup and RAG pipeline.
2.  **`openai-agents-sdk-gemini`**: For the Agent logic, tools, and guardrails.
3.  **`mcp-builder`**: For building the internal MCP server using `FastMCP` and best practices.
4.  **`rag-pipeline-builder`**: For Qdrant ingestion and retrieval logic.

**MANDATORY MCP SERVER USAGE:**
The plan MUST require the use of these MCP servers during implementation:
1.  **`context7`**: For verifying package names (`openai-chatkit`, `openai-agents`, `mcp`) and fetching docs.
2.  **`web-search`**: For researching Urdu NLP patterns and Web Speech API integration.
3.  **`zai-mcp-server` (Vision)**: For UI verification of the chat widget.
4.  **`chrome-devtools`**: For debugging WebSocket/SSE streams.

---

### 1. Architectural Vision
-   **Goal:** A seamless, conversational interface that acts as a "co-pilot" for agency management.
-   **Frontend:** Next.js 16 + `@openai/chatkit-react` + Web Speech API (for Voice).
-   **Backend:** FastAPI + `openai-chatkit` + `openai-agents`.
-   **Tool Layer:** An internal MCP Server (using `mcp` SDK) that exposes Service Layer logic to the Agent.
-   **Intelligence:** Gemini 2.0 (Logic) + Qdrant (Knowledge).

### 2. Required Plan Sections

#### A. Data Model & Schema
Define the schema for conversation history and user preferences.
-   **Conversation:** `id`, `user_id`, `created_at`, `title`.
-   **Message:** `id`, `conversation_id`, `role`, `content`, `created_at`.
-   **Preference:** `user_id`, `language` (en/ur), `voice_enabled`.

#### B. API Architecture (FastAPI Custom Backend)
Define the structure for the ChatKit custom server.
-   **Endpoints:**
    -   `POST /api/v1/chat/sessions`: Authenticate user and issue ChatKit token.
    -   `POST /api/v1/chat/respond`: Handle messages, orchestrate Agent, and stream NDJSON.
-   **Integration:** How the `CustomChatKitServer` wraps the `agents-sdk` Runner.

#### C. MCP Server Architecture (Using `mcp-builder`)
Define the internal MCP server using `FastMCP`.
-   **Location:** `backend/app/mcp/server.py`
-   **Tools:** Define explicit tools wrapping the Service Layer:
    -   `add_task`, `list_tasks`, `assign_task`, `complete_task`.
    -   `get_profitability`, `workload_summary`.
    -   `suggest_assignee` (AI Logic).
-   **Best Practices:** Use Pydantic models for inputs (as per `mcp-builder` skill).

#### D. AI & Agent Architecture
Define the Agent's brain using `openai-agents-sdk-gemini`.
-   **System Prompt:** Instructions for "TeamFlow Assistant" (Identity, Tone).
-   **Multi-language Instruction:** "If the user input is in Urdu or asks for Urdu, respond in Urdu."
-   **Tool Connection:** How the Agent connects to the internal MCP server defined in Section C.

#### E. Voice Command Strategy
-   **Frontend:** `useVoiceInput` hook using `window.SpeechRecognition`.
-   **UI:** Microphone button in the ChatKit input area.
-   **Flow:** Record Audio -> Text (Client-side) -> Send to ChatKit -> Agent Action.

#### F. Implementation Steps
Break down into 7-10 atomic steps:
1.  **Foundation:** Install `openai-chatkit`, `openai-agents`, `mcp` (verify with `context7`).
2.  **RAG Setup:** Ingest "Constitution" into Qdrant using `rag-pipeline-builder`.
3.  **MCP Server:** Implement `backend/app/mcp/server.py` using `mcp-builder` (FastMCP).
4.  **Agent Logic:** Implement `TeamFlowAgent` connecting to the MCP server.
5.  **Backend API:** Implement `CustomChatKitServer` in FastAPI.
6.  **Frontend:** Integrate `ChatProvider` and `Chat` widget (using `openai-chatkit-integration`).
7.  **Voice Feature:** Implement Web Speech API integration.
8.  **Testing:** Verify Urdu commands and Voice input via `chrome-devtools`.

### 3. Implementation Directives
-   "Use `mcp-builder` skill to generate the `FastMCP` server code structure."
-   "Use `context7` to fetch the latest **Official MCP SDK** documentation."
-   "Use `openai-chatkit-integration` skill to scaffold the `ChatPage.tsx` and `server.py`."
-   "Use `openai-agents-sdk-gemini` skill to configure the `AsyncOpenAI` client with Gemini's base URL."

---

## Output Requirement
Generate the `sp.plan` file. It must be a concrete, actionable blueprint that ensures all requirements (including Voice, Urdu, and MCP SDK) are met using the specified skills and custom backend architecture.

## Response snapshot

Successfully generated the implementation plan for TeamFlow AI Chatbot (Phase 3).

**Created Artifacts:**

1. **research.md** - Complete technical research covering:
   - SDK decisions (openai-chatkit, openai-agents, official MCP SDK)
   - Database schema design for conversations/messages
   - Qdrant RAG integration strategy
   - Frontend ChatKit React integration approach
   - Voice command implementation with Web Speech API
   - MCP tool definitions wrapping existing services
   - Urdu language support strategy
   - Security (RBAC) and performance optimizations

2. **data-model.md** - Complete data model with:
   - 3 new tables: conversations, messages, user_chat_preferences
   - ERD and relationships
   - Qdrant collection schema for RAG
   - State transitions and validation rules
   - Indexes and performance considerations
   - Migration strategy

3. **contracts/chat-api.yaml** - API contracts defining:
   - 5 endpoints (sessions, respond, history, preferences, health)
   - Streaming NDJSON response format
   - Error codes and rate limiting
   - TypeScript types for all data structures

4. **quickstart.md** - Developer setup guide with:
   - Prerequisites and environment setup
   - Backend and frontend startup instructions
   - Testing procedures
   - Troubleshooting guide

5. **plan.md** - Implementation blueprint with:
   - Technical context (Python 3.13+, TypeScript 5+, Node 20+)
   - Constitution check (all 8 gates passed ✅)
   - Project structure (backend/frontend directories)
   - Architecture diagram showing all layers
   - 9 implementation phases (Foundation → Deployment)
   - Skills and agents usage mapping
   - Success criteria validation table
   - Risk mitigation strategies

**Key Architectural Decisions:**
- Custom FastAPI backend (not OpenAI hosted ChatKit)
- Official MCP SDK with FastMCP for tool exposure
- Gemini 2.0 via OpenAI-compatible endpoint
- Qdrant for RAG knowledge base
- Web Speech API for client-side voice input
- 7-day conversation retention with scheduled cleanup

**Mandated Skills Referenced:**
- openai-chatkit-integration
- openai-agents-sdk-gemini
- mcp-builder
- rag-pipeline-builder

**Mandated MCP Servers Referenced:**
- context7 (package verification)
- web-search (Urdu NLP, Web Speech API research)
- chrome-devtools (SSE/WebSocket debugging)
- zai-mcp-server (UI verification)

## Outcome

- ✅ Impact: Created comprehensive implementation blueprint for Phase 3 AI Chatbot with all technical decisions resolved, including bonus features (Urdu support, voice input)
- 🧪 Tests: Constitution check passed all 8 gates; technical research resolved all unknowns; data model defined with 3 new tables and Qdrant collection; API contracts with 5 endpoints and streaming NDJSON
- 📁 Files: Created plan.md (458 lines), research.md (450 lines), data-model.md (280 lines), chat-api.yaml (200 lines), quickstart.md (220 lines), contracts/ directory
- 🔁 Next prompts: `/sp.tasks` - break down implementation blueprint into atomic, testable tasks for execution
- 🧠 Reflection: Plan successfully balances architectural depth with practical implementation guidance. The custom backend architecture using FastAPI + openai-chatkit + openai-agents + MCP SDK is clearly defined with specific file locations and skill mappings. Bonus features (Urdu, voice) are integrated into core phases rather than treated as add-ons. The 9-phase implementation approach follows a logical dependency order from foundation through deployment. All constitution gates passed with no violations requiring justification.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASSED all gates - constitution check (8/8), research completeness, data model validation, API contract definition, architecture feasibility
- Prompt variant (if applicable): N/A - standard /sp.plan workflow
- Next experiment (smallest change to try): N/A - plan complete, proceed to /sp.tasks for task breakdown
