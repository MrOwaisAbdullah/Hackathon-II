# OpenAI ChatKit Integration Guide

This document explains how TeamFlow integrates OpenAI ChatKit with a custom FastAPI backend.

## Architecture Overview

### What is ChatKit?

ChatKit is OpenAI's framework for building AI-powered chat interfaces with:
- Pre-built UI components (messages, input, widgets)
- Built-in streaming support
- Tool execution framework
- Rich widget support (cards, forms, lists)
- Self-hosted option for full control

### Our Implementation

TeamFlow uses the **self-hosted ChatKit** approach with:

```
Frontend (Next.js)          Backend (FastAPI)
     |                              |
     v                              v
ChatKit React Components  ->  ChatKit Server
     |                              |
     |                              v
     |                       AgentOrchestrator
     |                              |
     |                              v
     +------------------------> Gemini 2.0 Flash
                                   |
                                   v
                            MCP Tools (task mgmt)
                                   |
                                   v
                            Qdrant (RAG KB)
```

## Key Components

### Backend Files

1. **`app/chatkit/server.py`** - Main ChatKit server implementation
   - `TeamFlowChatKitServer` - Custom ChatKit server class
   - Integrates with `AgentOrchestrator` for AI responses
   - Supports RAG knowledge base queries
   - Handles tool execution and client tools

2. **`app/api/endpoints/chat.py`** - ChatKit endpoint
   - `POST /api/v1/chat/chatkit` - Main ChatKit protocol endpoint
   - Implements SSE streaming for real-time responses
   - Authenticates via `X-Session-Token` header

3. **`app/agents/orchestrator.py`** - AI orchestration
   - Processes messages through OpenAI Agents SDK
   - Manages conversation history
   - Executes MCP tools
   - Optional RAG integration

### Frontend Files

1. **`src/components/chat/ChatWidget.tsx`** - Chat widget component
   - Uses `@openai/chatkit-react` library
   - Connects to custom backend endpoint
   - Implements authentication headers
   - Floating toggle button

## Installation

### Backend Dependencies

```bash
# Add to pyproject.toml
openai-chatkit>=0.1.0

# Install
cd backend
uv pip install openai-chatkit
```

### Frontend Dependencies

```bash
# Already installed
"@openai/chatkit-react": "^1.4.0"
```

## Configuration

### Backend Setup

1. **Set environment variables** (`.env`):

```bash
# Database (for conversation persistence)
DATABASE_URL=postgresql://user:pass@host:5432/teamflow

# AI Services
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# RAG Service
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# Better Auth Secret
SECRET_KEY=your-secret-key-min-32-chars
```

2. **Data directories** (auto-created):

```bash
./data/chatkit/          # SQLite database
./data/chatkit/files/    # File attachments
```

### Frontend Setup

1. **Environment variables** (`.env.local`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. **Session token storage**:

The ChatWidget reads the Better Auth session token from:
```javascript
localStorage.getItem('better-auth.session_token')
```

## API Reference

### POST /api/v1/chat/chatkit

**Authentication:** `X-Session-Token` header

**Request Body:** ChatKit protocol (JSON)

**Response:** Server-Sent Events (SSE)

**Event Types:**

```typescript
// Text streaming
event: response.output_text.delta
data: {"delta": {"type": "text_delta", "text": "Hello"}}

// Tool call
event: response.tool_call.created
data: {"toolCall": {"id": "tool_123", "toolName": "add_task", ...}}

// Tool result
event: response.tool_call.done
data: {"result": "{...}"}

// Completion
event: response.done
data: {}

// Error
event: error
data: {"message": "Error details"}
```

## Usage Examples

### Basic Chat Widget

```tsx
import { ChatWidget } from '@/components/chat/ChatWidget'

export default function Page() {
  return (
    <>
      <h1>My App</h1>
      <ChatWidget apiUrl="http://localhost:8000" />
    </>
  )
}
```

### Custom Position

```tsx
<ChatWidget
  apiUrl="http://localhost:8000"
  position="bottom-left"
/>
```

### With Authentication

The widget automatically includes the Better Auth session token:

```tsx
// ChatWidget.tsx
const customFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const headers = {
    ...init?.headers,
    'X-Session-Token': localStorage.getItem('better-auth.session_token') || 'test-session',
  }
  return fetch(input, { ...init, headers })
}
```

## Architecture Decisions

### Why Self-Hosted ChatKit?

**Pros:**
- Full control over authentication
- Custom agent orchestration (AgentOrchestrator)
- RAG integration with Qdrant
- MCP tool execution
- Data residency (on-prem option)
- No OpenAI-hosted dependency

**Cons:**
- More setup required
- Need to maintain ChatKit server
- Must implement SSE streaming

### Why Not OpenAI-Hosted?

OpenAI-hosted ChatKit requires:
- JWT token generation workflow
- OpenAI API key exposure
- Limited customization
- Vendor lock-in

Our self-hosted approach gives us:
- Better Auth integration
- Custom AI models (Gemini, OpenRouter)
- RAG knowledge base
- Full control over data flow

## Troubleshooting

### Common Issues

#### 1. "Invalid client secret format"

**Cause:** Using OpenAI-hosted ChatKit instead of self-hosted

**Solution:** Ensure frontend uses `apiURL` not `apiKey`:
```tsx
const { control, ref } = useChatKit({
  apiURL: 'http://localhost:8000/api/v1/chat/chatkit',  // Correct
  // apiKey: 'sk-...'  // Wrong - this is for OpenAI-hosted
})
```

#### 2. CORS Errors

**Cause:** Backend not allowing frontend origin

**Solution:** Check CORS settings in `app/core/config.py`:
```python
frontend_url: str = Field(
    default="http://localhost:3000,http://localhost:8000",
)
```

#### 3. SSE Not Streaming

**Cause:** Buffering by nginx/proxy

**Solution:** Headers already set in endpoint:
```python
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}
```

#### 4. Authentication Failing

**Cause:** Missing or invalid session token

**Solution:** Check token in localStorage:
```javascript
console.log(localStorage.getItem('better-auth.session_token'))
```

### Debug Mode

Enable verbose logging:

```typescript
// ChatWidget.tsx
const customFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  console.log('[ChatWidget] Fetching:', input, 'with headers:', init?.headers)
  return fetch(input, init)
}
```

## Testing

### Backend Testing

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/api/v1/chat/chatkit \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: test-session" \
  -d '{"type": "user_message", "content": "Hello"}'
```

### Frontend Testing

```bash
# Start frontend
cd frontend
npm run dev

# Open http://localhost:3000/test-chatkit
```

### Integration Testing

1. Open browser console
2. Click chat button
3. Send message: "Hello, can you help me?"
4. Check for:
   - Connection status (green dot)
   - Streaming tokens
   - Tool execution (if applicable)
   - No errors in console

## Performance Considerations

### Backend

- **Streaming:** SSE for real-time token delivery
- **Database:** SQLite for ChatKit store (can be replaced with PostgreSQL)
- **Caching:** AgentOrchestrator maintains context window
- **Rate Limiting:** TODO: Implement rate limiting

### Frontend

- **React.memo:** Prevent unnecessary re-renders
- **useCallback:** Stable callbacks for hooks
- **Suspense:** Loading states for async operations

## Security

### Authentication

- Better Auth session validation
- X-Session-Token header required
- User-specific data isolation

### Authorization

- TODO: Implement RBAC in ChatKitServer
- TODO: Scope tools by user permissions

### Data Privacy

- RAG knowledge base access control
- No API keys in frontend
- Session token not exposed in logs

## Next Steps

### Phase 1: Core Integration (Current)

- [x] ChatKit server implementation
- [x] FastAPI endpoint with SSE
- [x] Frontend widget integration
- [ ] End-to-end testing

### Phase 2: Enhanced Features

- [ ] File upload support (images, documents)
- [ ] Widget rendering (cards, forms)
- [ ] Client tools (frontend actions)
- [ ] Multi-turn conversations

### Phase 3: Production Readiness

- [ ] Error handling and recovery
- [ ] Monitoring and observability
- [ ] Rate limiting and throttling
- [ ] Load testing and optimization

## References

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/guides/custom-chatkit)
- [OpenAI ChatKit GitHub](https://github.com/openai/chatkit-python)
- [Agents SDK Documentation](https://github.com/openai/agents-sdk)
- [Better Auth Documentation](https://www.better-auth.com)

## Support

For issues or questions:
1. Check browser console for errors
2. Check backend logs: `tail -f backend/logs/app.log`
3. Verify environment variables
4. Test with curl to isolate frontend vs backend issues
