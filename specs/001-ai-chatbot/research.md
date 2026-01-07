# Research: TeamFlow AI Chatbot (Phase 3)

**Feature**: 001-ai-chatbot | **Date**: 2025-01-06 | **Status**: Complete

## Overview

This document captures all technical research, decisions, and rationale for the Phase 3 AI Chatbot implementation. All "NEEDS CLARIFICATION" items from the plan template have been resolved through this research.

---

## 1. Core SDK & Package Decisions

### 1.1 OpenAI ChatKit (Python Backend)

**Decision**: Use `openai-chatkit` Python package for custom FastAPI backend integration.

**Rationale**:
- Custom backend requirement (Assumption #8) mandates self-hosted ChatKit server
- Python backend allows direct integration with existing FastAPI services
- Better control over authentication (Better Auth session validation)
- Enables streaming NDJSON responses compatible with `@openai/chatkit-react`

**Package Verification (via context7)**:
```
Package: openai-chatkit (Python)
Purpose: Custom ChatKit server implementation
Install: uv add openai-chatkit
Key Classes: ChatKitServer, StreamingConfig
```

**Alternatives Considered**:
- **OpenAI Hosted ChatKit**: Rejected - violates custom backend architecture mandate
- **WebSocket-only approach**: Rejected - ChatKit provides better abstraction for streaming, tool calls, and state management

---

### 1.2 OpenAI Agents SDK (with Gemini)

**Decision**: Use `openai-agents` Python SDK with AsyncOpenAI client pointing to Gemini's OpenAI-compatible endpoint.

**Rationale**:
- Agents SDK provides tool orchestration, guardrails, and state management
- Gemini 2.0 via OpenAI-compatible API offers cost advantages and strong reasoning
- Async support aligns with FastAPI's async patterns
- Built-in support for RAG context injection

**Configuration Pattern**:
```python
from openai import AsyncOpenAI
from openai.agents import Agent, Runner

# Configure for Gemini
client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY")
)

agent = Agent(
    name="teamflow-assistant",
    instructions="You are TeamFlow Assistant...",
    tools=tool_registry.get_all_tools()
)
```

**Alternatives Considered**:
- **Direct Gemini API**: Rejected - lacks tool orchestration and agent management
- **LangChain**: Rejected - heavier abstraction, more boilerplate for this use case

---

### 1.3 Official MCP SDK (FastMCP)

**Decision**: Use official `mcp` Python SDK with FastMCP for MCP server implementation.

**Rationale**:
- Official SDK provides standard protocol compliance
- FastMCP offers decorators and Pydantic integration
- Best practices documented in `.claude/skills/mcp-builder/`
- Enables clean tool definitions with input/output schemas

**Package Verification (via context7)**:
```
Package: mcp (Python, official)
Purpose: MCP server implementation
Install: uv add mcp
Key Classes: Server, FastMCP, Tool
Documentation: https://modelcontextprotocol.io/python-sdk
```

**Tool Pattern**:
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

class AddTaskInput(BaseModel):
    title: str
    priority: str = "MEDIUM"
    project_id: int | None = None

mcp_server = FastMCP("teamflow-tools")

@mcp_server.tool()
async def add_task(input: AddTaskInput) -> str:
    """Create a new task in TeamFlow."""
    # Call TaskService
    return f"Task created: {input.title}"
```

**Alternatives Considered**:
- **Custom HTTP tools**: Rejected - MCP provides standardization and better composability
- **LangChain tools**: Rejected - non-standard, adds unnecessary dependency

---

## 2. Database & Data Model

### 2.1 Conversation Storage

**Decision**: Add conversation/message tables to existing Neon PostgreSQL database.

**Schema Design**:
```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB,  -- Store tool call details
    created_at TIMESTAMP DEFAULT NOW()
);

-- User preferences for chat
CREATE TABLE user_chat_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    language TEXT NOT NULL DEFAULT 'en' CHECK (language IN ('en', 'ur')),
    voice_enabled BOOLEAN DEFAULT FALSE
);
```

**Rationale**:
- PostgreSQL already in use for Phase II
- UUIDs consistent with existing schema
- JSONB for flexible tool call storage
- 7-day retention implemented via scheduled cleanup job

**Alternatives Considered**:
- **Separate chat database**: Rejected - unnecessary complexity, cross-DB queries
- **In-memory only**: Rejected - requirement FR-020 mandates 7-day persistence

---

### 2.2 Qdrant Integration for RAG

**Decision**: Use Qdrant Cloud (or local Docker) for vector storage of project documentation.

**Collection Configuration**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url=os.getenv("QDRANT_URL"))

# Create collection
client.create_collection(
    collection_name="teamflow_kb",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)
```

**Document Ingestion Pipeline** (using `rag-pipeline-builder` skill):
1. **Extract**: Read .md files from `specs/`, `TEAMFLOW-PLAN.md`, constitution
2. **Chunk**: Split into 500-1000 character chunks with overlap
3. **Embed**: Use OpenAI `text-embedding-3-small` via AsyncOpenAI client
4. **Upsert**: Store in Qdrant with metadata (source, title, last_modified)

**Rationale**:
- Vector search enables semantic queries ("How do we handle auth errors?")
- Qdrant lightweight and fast for this scale
- Reuse existing OpenAI embeddings infrastructure

**Alternatives Considered**:
- **PostgreSQL pgvector**: Rejected - less performant for vector search
- **Pinecone**: Rejected - additional cost, Qdrant sufficient

---

## 3. Frontend Architecture

### 3.1 ChatKit React Integration

**Decision**: Use `@openai/chatkit-react` with `api.url` pointing to custom FastAPI backend.

**Configuration**:
```typescript
// app/layout.tsx
import { ChatProvider } from "@openai/chatkit-react";

export default function RootLayout({ children }) {
  return (
    <ChatProvider
      apiUrl="/api/v1/chat"
      accessToken={async () => {
        // Get from Better Auth session
        const session = await getSession();
        return session.chatToken;
      }}
    >
      {children}
    </ChatProvider>
  );
}
```

**Chat Widget Component**:
```typescript
// components/chat/ChatWidget.tsx
import { useChat } from "@openai/chatkit-react";
import { useVoiceInput } from "@/hooks/useVoiceInput";

export function ChatWidget() {
  const { messages, input, handleInputChange, submit } = useChat();
  const { isRecording, transcript, startRecording, stopRecording } = useVoiceInput();

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[500px]">
      {/* Chat UI with voice button */}
    </div>
  );
}
```

**Rationale**:
- ChatKit provides battle-tested streaming, typing indicators, and state management
- Custom backend maintains control over authentication and tool execution
- React hooks align with existing Next.js patterns

**Alternatives Considered**:
- **Custom WebSocket implementation**: Rejected - reinventing the wheel, more surface area for bugs
- **Vercel AI SDK**: Rejected - less mature for multi-turn conversations with tools

---

### 3.2 Voice Command Integration

**Decision**: Implement `useVoiceInput` hook using Web Speech API for client-side speech-to-text.

**Implementation**:
```typescript
// hooks/useVoiceInput.ts
export function useVoiceInput() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");

  const startRecording = () => {
    const recognition = new (window as any).SpeechRecognition();
    recognition.lang = "en-US"; // or "ur-PK" for Urdu
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      setTranscript(event.results[0][0].transcript);
    };

    recognition.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    recognition.stop();
    setIsRecording(false);
  };

  return { isRecording, transcript, startRecording, stopRecording };
}
```

**Rationale**:
- Client-side speech-to-text reduces backend load
- Web Speech API built into modern browsers (no additional cost)
- Text sent to backend via normal ChatKit flow (no audio streaming needed)

**Urdu Support**:
- Use `lang = "ur-PK"` for Urdu transcription
- Browser support varies (Chrome best, Firefox experimental)
- Fallback to typing if not supported

**Alternatives Considered**:
- **OpenAI Whisper API**: Rejected - adds latency and cost
- **Server-side speech recognition**: Rejected - unnecessary complexity

---

## 4. MCP Server Architecture

### 4.1 Tool Definitions

**Decision**: Define MCP tools that wrap existing Service Layer methods from Phase II.

**Tool List**:
```python
# backend/app/mcp/server.py

@mcp_server.tool()
async def add_task(title: str, priority: str, project_id: int | None) -> str:
    """Create a new task with title, priority, and optional project assignment."""
    task = await TaskService.create_task(
        title=title,
        priority=priority,
        project_id=project_id
    )
    return f"Task '{task.title}' created with ID {task.id}"

@mcp_server.tool()
async def list_tasks(status: str | None = None, project_id: int | None = None) -> list[dict]:
    """List tasks with optional filters for status and project."""
    tasks = await TaskService.list_tasks(status=status, project_id=project_id)
    return [task.model_dump() for task in tasks]

@mcp_server.tool()
async def assign_task(task_id: int, assignee_id: int) -> str:
    """Assign a task to a user."""
    task = await TaskService.update_task(
        task_id=task_id,
        assignee_id=assignee_id
    )
    return f"Task assigned to {task.assignee.name}"

@mcp_server.tool()
async def complete_task(task_id: int) -> str:
    """Mark a task as complete."""
    await TaskService.update_task(task_id=task_id, status="DONE")
    return f"Task {task_id} marked as complete"

@mcp_server.tool()
async def get_profitability(project_id: int) -> dict:
    """Calculate project profitability (revenue, cost, profit, margin)."""
    profit = await AnalyticsService.get_project_profitability(project_id)
    return profit.model_dump()

@mcp_server.tool()
async def workload_summary(team_id: int) -> list[dict]:
    """Get workload overview for all team members."""
    return await AnalyticsService.get_team_workload(team_id)

@mcp_server.tool()
async def suggest_assignee(task_id: int) -> dict:
    """AI suggests the best person to assign a task based on skills and workload."""
    task = await TaskService.get_task(task_id)
    candidates = await UserService.get_team_members(task.project.team_id)

    # AI reasoning: evaluate skills + current workload
    # Return {user_id, reasoning, workload_score}
    ...
```

**Rationale**:
- Wrapping services maintains single responsibility
- Pydantic models ensure type safety
- Async/await for non-blocking operations

---

### 4.2 Agent-MCP Integration

**Decision**: Agent calls MCP tools via direct Python function calls (not stdio/HTTP).

**Pattern**:
```python
# backend/app/agents/orchestrator.py

from openai.agents import Agent, Runner
from app.mcp.server import mcp_server

class AgentOrchestrator:
    def __init__(self):
        # Extract tools from MCP server
        self.tools = mcp_server.get_tools()

        self.agent = Agent(
            name="teamflow-assistant",
            instructions=self._get_system_prompt(),
            tools=self.tools
        )
        self.runner = Runner(agent=self.agent)

    def _get_system_prompt(self) -> str:
        return """
        You are TeamFlow Assistant, an AI co-pilot for agency task management.

        Your capabilities:
        - Create, assign, and complete tasks via natural language
        - Query project profitability and team workload
        - Answer questions about project documentation (RAG)

        Multi-language support:
        - If user speaks in Urdu, respond in Urdu (Roman script).
        - If user asks for Urdu, switch to Urdu.

        Tone: Professional, concise, helpful.

        Always ask for clarification if a command is ambiguous.
        """

    async def process_message(self, user_message: str, conversation_id: str) -> AsyncIterator[str]:
        """Stream agent response."""
        # Get conversation history
        history = await ChatService.get_history(conversation_id)

        # Run agent
        result = await self.runner.run(
            user_message,
            context=history
        )

        # Stream response
        async for chunk in result:
            yield chunk.content
```

**Rationale**:
- Direct function calls faster than stdio/HTTP for local MCP server
- Simplifies debugging and testing
- Maintains type safety

**Alternatives Considered**:
- **stdio MCP transport**: Rejected - unnecessary overhead for same-process server
- **HTTP MCP transport**: Rejected - adds serialization overhead

---

## 5. Bonus Features Implementation

### 5.1 Urdu Language Support

**Decision**: Implement Urdu detection and response via language detection and system prompt adjustments.

**Detection Logic**:
```python
def detect_language(text: str) -> str:
    """Detect if text is Urdu (basic heuristic)."""
    urdu_chars = set("ابپتٹثجچحخدذرڈذژژسشصضطظعغفقکگلمنوہی")
    text_chars = set(text.lower())

    # If >30% characters are Urdu, classify as Urdu
    if len(text_chars & urdu_chars) / len(text_chars) > 0.3:
        return "ur"
    return "en"
```

**System Prompt Adjustment**:
```python
if detected_language == "ur":
    system_prompt += "\n\nRespond in Urdu (Roman script). Be concise and professional."
```

**Rationale**:
- Basic character-based detection sufficient for MVP
- Roman Urdu widely used in Pakistan (more practical than Arabic script)
- Can upgrade to proper ML detector if needed

**Alternatives Considered**:
- **langdetect library**: Rejected - additional dependency, overkill
- **Client-side language header**: Rejected - not reliable (user may type mixed languages)

---

### 5.2 Voice Command UX

**Decision**: Add microphone button to ChatKit input area with visual feedback for recording state.

**UI Flow**:
1. User clicks microphone icon
2. Icon pulses red while recording
3. User speaks (appears as real-time transcript below input)
4. User stops recording (auto-stop after 5s silence)
5. Transcript populated in input field
6. User can edit before sending (or re-record)

**Accessibility**:
- Keyboard shortcut: `Ctrl+Shift+V` to toggle recording
- Screen reader announcement: "Recording started/stopped"
- Visual fallback: If Web Speech API unsupported, hide button

**Rationale**:
- Voice is supplementary to typing (not replacement)
- Edit-before-send prevents errors
- Keyboard shortcuts for power users

---

## 6. Security & Authentication

### 6.1 Chat Session Authentication

**Decision**: Validate Better Auth session before issuing ChatKit token.

**Flow**:
```python
# backend/app/api/chat.py

@router.post("/api/v1/chat/sessions")
async def create_chat_session(
    request: Request
) -> ChatSessionResponse:
    # Validate Better Auth session cookie
    session = await better_auth.get_session(request)

    if not session:
        raise HTTPException(401, "Not authenticated")

    # Generate ChatKit-specific token
    chat_token = generate_chat_token(
        user_id=session.user.id,
        role=session.user.role,
        expires_in=7 * 24 * 3600  # 7 days
    )

    # Create or get active conversation
    conversation = await ChatService.get_or_create_conversation(
        user_id=session.user.id
    )

    return ChatSessionResponse(
        token=chat_token,
        conversation_id=conversation.id
    )
```

**Rationale**:
- Leverages existing Better Auth (Phase II)
- No separate login for chat (FR-019)
- Token scoped to chat operations only

---

### 6.2 RBAC Enforcement

**Decision**: Check user roles before executing MCP tools.

**Pattern**:
```python
@mcp_server.tool()
async def assign_task(task_id: int, assignee_id: int, user_context: UserContext) -> str:
    """Assign a task to a user. Requires Manager or Admin role."""

    # RBAC check
    if user_context.role not in ["admin", "manager"]:
        raise PermissionError("Only managers can assign tasks")

    # Proceed with assignment
    ...
```

**Rationale**:
- Prevents unauthorized task modifications
- Aligns with clarification session decision (full RBAC)
- User context injected by Agent orchestrator

---

## 7. Performance & Scalability

### 7.1 Response Time Targets

**Goals** (from spec success criteria):
- Streaming begins within 2 seconds (SC-007)
- Knowledge base queries < 3 seconds (SC-003)
- Chat availability 99% uptime (SC-006)

**Strategies**:
1. **Streaming**: Use NDJSON for incremental responses
2. **Caching**: Cache Qdrant embeddings (document content rarely changes)
3. **Async**: All I/O operations async (DB, Qdrant, external APIs)
4. **Connection Pooling**: Reuse DB and Qdrant connections

---

### 7.2 Data Retention

**Decision**: Implement 7-day conversation retention via scheduled cleanup job.

**Implementation**:
```python
# backend/app/jobs/cleanup_old_conversations.py

@cron.schedule(hourly)
async def cleanup_old_conversations():
    """Delete conversations older than 7 days."""
    cutoff = datetime.now() - timedelta(days=7)

    await db.execute(
        "DELETE FROM messages WHERE created_at < :cutoff",
        {"cutoff": cutoff}
    )

    await db.execute(
        "DELETE FROM conversations WHERE id NOT IN (SELECT DISTINCT conversation_id FROM messages)"
    )
```

**Rationale**:
- Privacy: Minimize stored conversation data
- Cost: Reduce DB storage
- Performance: Smaller tables = faster queries

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Coverage**:
- MCP tools: Mock services, test input validation
- Agent logic: Mock tool calls, test response generation
- Language detection: Test edge cases (mixed, empty, special chars)

**Framework**: `pytest` + `pytest-asyncio`

---

### 8.2 Integration Tests

**Scenarios**:
1. End-to-end chat flow (from FastAPI to Agent to MCP tools)
2. RAG retrieval (query → Qdrant → context injection)
3. Multi-language (Urdu input → Urdu output)

**Framework**: `httpx.AsyncClient` for FastAPI testing

---

### 8.3 E2E Tests

**Critical Journeys**:
1. "Create task via chat" → Verify task in DB
2. "Assign task to Sarah" → Verify assignee updated
3. "How do we handle auth errors?" → Verify RAG response

**Framework**: Playwright (Chrome DevTools MCP for debugging)

---

## 9. Implementation Dependencies

### Required Skills (Mandatory)

| Skill | Purpose | Location |
|-------|---------|----------|
| `openai-chatkit-integration` | ChatKit backend/frontend setup | `.claude/skills/` |
| `openai-agents-sdk-gemini` | Agent orchestration with Gemini | `.claude/skills/` |
| `mcp-builder` | MCP server best practices | `.claude/skills/mcp-builder/` |
| `rag-pipeline-builder` | Qdrant ingestion pipeline | `.claude/skills/` |

### Required Agents

| Agent | Purpose | Location |
|-------|---------|----------|
| `openai-agents-sdk-specialist` | Agent implementation guidance | `.claude/agents/` |
| `rag-specialist` | RAG pipeline debugging | `.claude/agents/` |

---

## 10. Open Questions & Risks

### 10.1 Open Questions

**None** - All technical decisions resolved.

---

### 10.2 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gemini API rate limits | Medium | Implement queuing, fallback to OpenAI GPT-4 |
| Web Speech API browser support | Low | Graceful degradation to typing-only |
| Qdrant downtime | Medium | Cache embeddings, fallback to direct DB query |
| Urdu detection accuracy | Low | Add "force Urdu" toggle for users |

---

## 11. Next Steps

1. **Verify Packages**: Use `context7` MCP to confirm latest versions of `openai-chatkit`, `openai-agents`, `mcp`
2. **Generate Data Model**: Create `data-model.md` with complete schema
3. **Generate Contracts**: Create API contracts in `contracts/` directory
4. **Update Plan**: Fill `plan.md` with implementation blueprint
5. **Proceed to Tasks**: Run `/sp.tasks` to break down implementation steps

---

**Research Status**: ✅ Complete

All technical unknowns resolved. Ready for Phase 1 (Design & Contracts).
