# Phase 3: TeamFlow AI Chatbot Specification Prompt

You are acting as the **Lead AI Architect** for TeamFlow. Your goal is to generate the **Specify (Requirement Specification)** for Phase 3 of the project.

## Context
We are executing **Phase 3: AI-Powered Task Chatbot** of the TeamFlow Agency CRM.
We are transforming the CRM into an intelligent agentic system.
We utilize a **Custom Backend** approach for OpenAI ChatKit to leverage non-OpenAI models (Gemini) and our own RAG pipeline (Qdrant).

## Directive
Run the `sp.specify` process to generate the requirements file (`specs/phase3-spec.md`).

**CRITICAL SKILL USAGE:**
You MUST explicitly mandate the use of the following specialized skills and agents in the implementation plan:
1.  **`openai-chatkit-integration`**: For setting up the FastAPI custom backend, frontend widget, and RAG pipeline integration.
2.  **`openai-agents-sdk-gemini`**: For implementing the Agent logic, tools, and guardrails using the OpenAI Agents SDK with Gemini models.
3.  **`openai-agents-sdk-specialist`**: The persona responsible for guiding the agent implementation.

**MANDATORY MCP SERVER USAGE:**
The specification must require the use of the following MCP servers during implementation:
1.  **`context7`**:
    *   **Verify Package Names**: Check PyPI and GitHub to confirm the exact package names and compatible versions for `openai-chatkit` (Python) and `openai-agents` (formerly agents-sdk).
    *   **Fetch Docs**: Retrieve latest API references for `@openai/chatkit-react` and `qdrant-client`.
2.  **`web-search`**: Research best practices for Gemini 2.5 prompting and advanced RAG patterns if documentation is insufficient.
3.  **`zai-mcp-server` (Vision)**: Analyze screenshots of the ChatKit UI during testing to verify styling and layout alignment with the "Eco-Modern" theme.
4.  **`chrome-devtools`**: Validate frontend-backend communication (WebSocket/SSE streams) and debug ChatKit widget integration.

---

### 1. Project Overview
- **Name:** TeamFlow AI (Phase 3)
- **Type:** RAG-Powered Agentic Chatbot
- **Stack:**
    - **Frontend:** Next.js 16 + `@openai/chatkit-react` (Advanced Mode).
    - **Backend:** FastAPI + `openai-chatkit` (Python) + `openai-agents` (Python).
    - **Intelligence:** Google Gemini 2.5 (via OpenAI Compat) + Qdrant Vector DB.
- **Goal:** Enable users to manage tasks, query project data, and get AI recommendations via natural language.

### 2. User Stories & Core Features

#### A. Conversational Task Management
*As a Project Manager, I want to manage tasks via chat so I can stay in flow...*
- **Create Task:** "Add a high priority task to fix the navbar for the Acme project."
- **Assign Task:** "Assign the database migration to the best backend dev." (Requires AI reasoning).
- **Query Status:** "What tasks are currently blocked or overdue?"

#### B. RAG & Knowledge Retrieval
*As a Team Member, I want to ask questions about project context...*
- **Context Query:** "What were the design requirements for the landing page?" (Retrieves from Qdrant).
- **Profitability:** "Are we over budget on Project X?" (Calculates via Tool).

#### C. AI Reasoning & Recommendations
*As an Agency Owner, I want intelligent insights...*
- **Assignee Suggestion:** AI analyzes team skills and workload to suggest the best person.
- **Workload Analysis:** "Who is over capacity this week?"

### 3. Technical Architecture (The "Custom Backend" Mandate)

**Constraint:** The specification must enforce the **Custom Backend** pattern defined in the `openai-chatkit-integration` skill.

#### Backend (FastAPI)
- **Endpoint:** `POST /api/v1/chat/respond` (Streams NDJSON).
- **Session Endpoint:** `POST /api/v1/chat/sessions`.
    - **Auth Integration:** This endpoint MUST validate the existing **Better Auth** session (cookie/header) before issuing a ChatKit token. Do NOT create a separate user system for ChatKit.
- **Orchestrator:** A central `ChatKitServer` implementation that:
    1.  Embeds the user query (via `rag-pipeline-builder` logic).
    2.  Retrieves context from Qdrant.
    3.  Initializes an Agent (via `openai-agents-sdk-gemini`) with tools and context.
    4.  Streams the response back to the frontend.

#### AI Tools (MCP Layer / Service Wrapping)
The Agent must have access to Python functions (Tools) that **wrap our existing Service Layer**:
- **Tool:** `add_task` → Calls `TaskService.create_task(...)`
- **Tool:** `assign_task` → Calls `TaskService.update_task(..., assignee_id=...)`
- **Tool:** `list_tasks` → Calls `TaskService.list_tasks(...)`
- **Tool:** `get_project_stats` → Calls `AnalyticsService.get_project_stats(...)`
- **Tool:** `search_knowledge_base` → Queries Qdrant directly.

#### Frontend (ChatKit)
- **Integration:** Use `@openai/chatkit-react` with `api.url` pointing to our FastAPI server.
- **UI:** A floating widget or sidebar panel (integrated into the existing Layout).
- **Theme:** Must inherit the "Eco-Modern" theme (Lime/Black) defined in Phase 2.

### 4. Implementation Strategy
1.  **Research (context7):** Confirm `openai-agents` package name and `openai-chatkit` compatibility.
2.  **Setup:** Install verified packages via `uv`.
3.  **Infrastructure:** Provision Qdrant collection using `rag-pipeline-builder` scripts.
4.  **Backend:** Implement `CustomChatKitServer` in `backend/app/api/chat.py`, wrapping existing Services as Tools.
5.  **Agent:** Define the `TeamFlowAgent` with instructions and tool definitions.
6.  **Frontend:** Add `ChatProvider` to the Next.js app layout with proper authentication token passing.
7.  **Validation (chrome-devtools/vision):** Test chat flow and verify UI.

### 5. Acceptance Criteria Examples
- **Scenario: Complex Command**
    - **Input:** "Create a task 'Review PRs', assign it to Sarah, and tag it as Urgent."
    - **System:** Calls `create_task` tool with correct arguments (mapped from NL to Service Layer).
    - **Output:** "Created task #123 'Review PRs' assigned to Sarah (Urgent)."
- **Scenario: RAG Query**
    - **Input:** "How do we handle auth errors?"
    - **System:** Searches Qdrant -> Finds "Constitution.md" chunk -> Generates answer.
    - **Output:** "According to the constitution, auth errors should raise 401 exceptions..."

---

## Output Requirement
Generate the `specs/phase3-spec.md` file. Ensure it strictly references the **Custom Backend** architecture and the use of **Gemini** via the Agents SDK compatibility layer.