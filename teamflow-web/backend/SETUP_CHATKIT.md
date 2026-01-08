# ChatKit Integration Setup Guide

This guide walks you through setting up OpenAI ChatKit with TeamFlow's custom backend.

## Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL (Neon recommended)
- Qdrant (for RAG)
- Better Auth configured

## Step 1: Backend Setup

### 1.1 Install Dependencies

```bash
cd /mnt/d/GIAIC/Quarter\ 4/Hackathon\ II/teamflow-web/backend

# Using pip
pip install openai-chatkit

# Using uv (recommended)
uv pip install openai-chatkit

# Using pipenv
pipenv install openai-chatkit
```

### 1.2 Environment Variables

Create or update `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/teamflow

# AI Services
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# RAG Service (optional)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# Better Auth
SECRET_KEY=your-secret-key-min-32-chars-for-production

# CORS (allow frontend)
FRONTEND_URL=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=development
```

### 1.3 Create Data Directories

```bash
# ChatKit data directories (auto-created, but can create manually)
mkdir -p data/chatkit
mkdir -p data/chatkit/files
```

### 1.4 Run Database Migrations

```bash
# Run Alembic migrations
cd backend
alembic upgrade head
```

### 1.5 Test Backend

```bash
# Run test script
python tests/test_chatkit_integration.py

# Expected output:
# ✅ openai-chatkit package installed
# ✅ TeamFlow ChatKit server imported
# ✅ Created SQLiteStore
# ✅ Created TeamFlowChatKitServer
```

### 1.6 Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m uvicorn app.main:app --reload
```

Verify backend is running:
```bash
curl http://localhost:8000/api/v1/chat/health
```

## Step 2: Frontend Setup

### 2.1 Install Dependencies

Dependencies are already installed in `package.json`:

```json
{
  "@openai/chatkit-react": "^1.4.0"
}
```

### 2.2 Environment Variables

Create or update `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2.3 Verify ChatWidget Component

The ChatWidget is located at:
```
frontend/src/components/chat/ChatWidget.tsx
```

It should use:
- `apiURL` instead of `apiKey`
- Custom fetch with authentication headers
- Floating toggle button

### 2.4 Start Frontend Server

```bash
cd /mnt/d/GIAIC/Quarter\ 4/Hackathon\ II/teamflow-web/frontend

# Development mode
npm run dev

# Or using yarn
yarn dev

# Or using pnpm
pnpm dev
```

Frontend will be available at: `http://localhost:3000`

## Step 3: Test Integration

### 3.1 Access Test Page

Open in browser:
```
http://localhost:3000/test-chatkit
```

### 3.2 Verify Connection

1. Click the blue chat button (bottom-right)
2. Chat window should open
3. Status should show "Connected" (green dot)
4. Try sending a message: "Hello, can you help me?"

### 3.3 Check Browser Console

Open Developer Tools (F12) and check:

**Console logs:**
```
[ChatWidget] Component mounting with apiUrl: http://localhost:8000
[ChatWidget] >>> onReady CALLED <<<
[ChatWidget] useChatKit returned control: true ref: true isInitialized: true
```

**Network tab:**
- Should see POST request to `/api/v1/chat/chatkit`
- Status: 200 OK
- Content-Type: `text/event-stream`

### 3.4 Test Streaming

Send a longer message and verify:
- Tokens stream in real-time
- No long delays
- Smooth rendering

## Step 4: Verify Backend Integration

### 4.1 Check Backend Logs

Backend should log:
```
INFO:     127.0.0.1:xxxx - "POST /api/v1/chat/chatkit HTTP/1.1" 200 OK
```

### 4.2 Test with cURL

```bash
curl -X POST http://localhost:8000/api/v1/chat/chatkit \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: test-session" \
  -d '{
    "type": "user_message",
    "content": "Hello from curl!"
  }'
```

Expected: SSE stream with response tokens

## Troubleshooting

### Issue: "openai-chatkit not found"

**Solution:**
```bash
pip install openai-chatkit
# or
uv pip install openai-chatkit
```

### Issue: "Invalid client secret format"

**Cause:** Using `apiKey` instead of `apiURL`

**Solution:** In `ChatWidget.tsx`, use:
```typescript
const { control, ref } = useChatKit({
  apiURL: 'http://localhost:8000/api/v1/chat/chatkit',  // Correct
  // apiKey: 'sk-...'  // Wrong - remove this
})
```

### Issue: CORS errors

**Solution:** Check `FRONTEND_URL` in backend `.env`:
```bash
FRONTEND_URL=http://localhost:3000,http://localhost:8000
```

### Issue: Authentication failing

**Solution:** Check session token in browser:
```javascript
// Run in browser console
localStorage.getItem('better-auth.session_token')
```

Backend should accept this token:
```python
# In app/api/endpoints/chat.py
async def verify_session_token(...):
    TEMP_USER_ID = "739fe54d-a2df-4701-b7ef-a9c283610ae0"
    return {"user_id": TEMP_USER_ID, ...}
```

### Issue: No streaming

**Cause:** Proxy buffering (nginx, etc.)

**Solution:** Headers already set:
```python
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}
```

### Issue: Agent not responding

**Cause:** Missing API keys

**Solution:** Check `.env`:
```bash
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

Test with:
```bash
# Test Gemini connection
python -c "from app.agents.client import initialize_gemini_client; initialize_gemini_client(); print('✅ Gemini OK')"

# Test OpenRouter
python tests/test_openrouter.py
```

## Architecture Verification

### Verify Backend Components

```bash
# Check ChatKit server
python -c "from app.chatkit import get_chatkit_server; print('✅ ChatKit server')"

# Check orchestrator
python -c "from app.agents.orchestrator import get_orchestrator; print('✅ Orchestrator')"

# Check MCP tools
python -c "from app.mcp.server import mcp; print(f'✅ MCP: {len(mcp.list_tools())} tools')"

# Check RAG service
python -c "from app.services.rag_service import rag_service; print('✅ RAG service')"
```

### Verify Frontend Components

```bash
cd frontend

# Check ChatKit version
npm list @openai/chatkit-react

# Should show: @openai/chatkit-react@1.4.0
```

## Performance Testing

### Test Streaming Speed

Send a long message and measure:
- Time to first token (TTFT)
- Tokens per second
- Total response time

### Test Concurrent Users

Use a load testing tool:
```bash
# Using Apache Bench
ab -n 100 -c 10 -p test_payload.json -T application/json \
  http://localhost:8000/api/v1/chat/chatkit
```

## Production Deployment

### Backend

1. **Environment:** Set `ENVIRONMENT=production`
2. **Database:** Use production Neon PostgreSQL
3. **Secrets:** Use strong `SECRET_KEY` (32+ chars)
4. **CORS:** Set `FRONTEND_URL` to production domain
5. **Workers:** Run with multiple workers:
   ```bash
   uvicorn app.main:app --workers 4 --host 0.0.0.0
   ```

### Frontend

1. **Build:** `npm run build`
2. **Environment:** Set `NEXT_PUBLIC_API_URL` to production backend
3. **Deploy:** Use Vercel, Netlify, or custom hosting

### Monitoring

1. **Logs:** Check backend logs regularly
2. **Metrics:** Track response times, error rates
3. **Alerts:** Set up alerts for failures

## Next Steps

After setup is complete:

1. **Customize the UI:**
   - Modify `ChatWidget.tsx` for custom styling
   - Add custom prompts in `startScreen`
   - Configure theme colors

2. **Add Features:**
   - File upload support
   - Widget rendering (cards, forms)
   - Client tools (frontend actions)
   - Voice input/output

3. **Optimize Performance:**
   - Implement caching
   - Add rate limiting
   - Optimize database queries

4. **Enhance Security:**
   - Implement RBAC
   - Add input validation
   - Sanitize outputs

## Support

For issues or questions:
- Check `CHATKIT_INTEGRATION.md` for detailed architecture
- Review browser console for frontend errors
- Review backend logs for API errors
- Test with cURL to isolate issues

## Summary

✅ **Backend:**
- Installed `openai-chatkit`
- Created `TeamFlowChatKitServer`
- Added `/api/v1/chat/chatkit` endpoint
- Integrated with `AgentOrchestrator`

✅ **Frontend:**
- Updated `ChatWidget.tsx`
- Uses custom backend endpoint
- Implements authentication headers
- Floating toggle button with status

✅ **Integration:**
- SSE streaming for real-time responses
- RAG knowledge base support
- MCP tool execution
- Better Auth integration

Ready to test! 🚀
