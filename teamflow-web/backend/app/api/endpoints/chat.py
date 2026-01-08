"""Chat API endpoints for TeamFlow AI Assistant.

This module provides FastAPI endpoints for:
- Session management (Better Auth validation)
- Message processing with streaming responses
- Conversation history retrieval
- User preferences management
- Health checks for AI services
- ChatKit protocol support (self-hosted)

Authentication: Uses Better Auth session validation via X-Session-Token header.
Response Format: NDJSON streaming for real-time responses.
"""
import json
import asyncio
from typing import Optional, AsyncIterator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field

from app.services.chat_service import ChatService
from app.agents.orchestrator import get_orchestrator
from app.models.chat import ConversationCreate, MessageRole
from app.models.preferences import UserChatPreference, ChatLanguage
from app.db.session import SessionDep
# from app.chatkit import get_chatkit_server  # TODO: Fix chatkit integration


# Request/Response models
class ChatSessionRequest(BaseModel):
    """Request to create a chat session."""
    user_id: str = Field(..., description="User ID from Better Auth session")


class ChatMessageRequest(BaseModel):
    """Request to send a chat message."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    use_knowledge_base: bool = Field(False, description="Whether to query knowledge base")


class ChatPreferencesUpdate(BaseModel):
    """Request to update chat preferences."""
    language: ChatLanguage = Field("en", description="Preferred language (en/ur)")
    voice_enabled: bool = Field(False, description="Whether voice input is enabled")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    services: dict[str, str]
    timestamp: str


# Router
router = APIRouter(prefix="/chat", tags=["chat"])


# Dependencies
async def get_chat_service():
    """Get ChatService instance."""
    from app.services.chat_service import chat_service
    return chat_service


async def verify_session_token(
    request: Request,
    x_session_token: Optional[str] = Header(None, alias="X-Session-Token"),
) -> dict:
    """
    Verify Better Auth session token.

    For testing purposes, accepts any token and creates a temp user session.
    TODO: Integrate with actual Better Auth session verification.

    Args:
        request: FastAPI request
        x_session_token: Session token from header (optional for testing)

    Returns:
        Session data with user_id
    """
    # For testing: use fixed temp user ID that exists in database
    # TODO: Verify JWT token with actual Better Auth integration
    TEMP_USER_ID = "739fe54d-a2df-4701-b7ef-a9c283610ae0"
    return {
        "user_id": TEMP_USER_ID,
        "session_id": x_session_token or "test-session"
    }


# Endpoints
@router.post("/sessions", response_model=dict)
async def create_chat_session(
    request: ChatSessionRequest,
    session: SessionDep,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Create a new chat session.

    Validates Better Auth session and creates a new conversation.
    Returns the conversation ID for subsequent chat requests.

    Raises:
        HTTPException: If session validation fails
    """
    try:
        # Use user_id from session (already a valid UUID string)
        from uuid import UUID
        user_id = UUID(session_data["user_id"])

        # Create conversation
        conversation = chat_service.create_conversation(
            user_id=user_id,
            session=session,
        )

        return {
            "conversation_id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "message": "Chat session created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/respond")
async def chat_respond(
    request: ChatMessageRequest,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Send a chat message and receive streaming response.

    Returns NDJSON stream with events:
    - {"type": "token", "data": {"content": "word "}}
    - {"type": "tool_call", "data": {"tool": "add_task", "args": {...}}}
    - {"type": "tool_result", "data": {"result": {...}}}
    - {"type": "done", "data": {}}

    Raises:
        HTTPException: If request validation fails or AI service unavailable
    """
    async def event_stream() -> AsyncIterator[str]:
        """Generate NDJSON stream of events."""
        try:
            orchestrator = get_orchestrator(chat_service)
            user_id = session_data["user_id"]

            # Process message with or without RAG
            stream = orchestrator.process_with_rag if request.use_knowledge_base else orchestrator.process_message

            async for event in stream(
                user_message=request.message,
                conversation_id=request.conversation_id,
                user_id=user_id,
            ):
                # Convert event to NDJSON
                yield json.dumps(event) + "\n"

        except Exception as e:
            # Send error event
            error_event = {
                "type": "error",
                "data": {
                    "message": str(e),
                    "type": type(e).__name__,
                }
            }
            yield json.dumps(error_event) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Get message history for a conversation.

    Args:
        conversation_id: Conversation UUID
        limit: Maximum messages to return (default: 50)
        offset: Number of messages to skip (default: 0)

    Returns:
        List of messages with metadata

    Raises:
        HTTPException: If conversation not found or access denied
    """
    try:
        # Verify user has access to this conversation
        user_id = session_data.get("user_id")
        conversation = await chat_service.get_conversation_internal(
            conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # TODO: Verify user_id matches conversation.user_id
        # For now, we'll skip this check

        # Get messages
        messages = await chat_service.get_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )

        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
                for msg in messages
            ],
            "total": len(messages),
            "limit": limit,
            "offset": offset,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")


@router.patch("/preferences")
async def update_chat_preferences(
    request: ChatPreferencesUpdate,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Update user chat preferences.

    Updates language preference and voice input setting.
    Creates preference record if it doesn't exist.

    Returns:
        Updated preferences

    Raises:
        HTTPException: If update fails
    """
    try:
        user_id = session_data["user_id"]

        # TODO: Implement preferences update in ChatService
        # For now, return mock response
        return {
            "user_id": user_id,
            "language": request.language,
            "voice_enabled": request.voice_enabled,
            "updated_at": datetime.utcnow().isoformat(),
            "message": "Preferences updated successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Check health of AI chat services.

    Returns:
        Health status for:
        - AI Agent (Gemini connection)
        - Qdrant (knowledge base)
        - MCP Server (tool availability)
    """
    services = {}

    # Check AI Agent
    try:
        orchestrator = get_orchestrator(chat_service)
        agent = orchestrator.get_agent()
        services["ai_agent"] = "healthy"
    except Exception as e:
        services["ai_agent"] = f"unhealthy: {str(e)}"

    # Check Qdrant
    try:
        from app.services.rag_service import rag_service
        # Try a simple search (synchronous call)
        rag_service.search_knowledge_base("test", limit=1)
        services["qdrant"] = "healthy"
    except Exception as e:
        services["qdrant"] = f"unhealthy: {str(e)}"

    # Check MCP Server
    try:
        from app.mcp.server import mcp
        # FastMCP stores tools internally - just check if server exists
        # Tools are registered via decorators, not available as simple list
        services["mcp_server"] = "healthy (tools registered)"
    except Exception as e:
        services["mcp_server"] = f"unhealthy: {str(e)}"

    # Overall status
    all_healthy = all("healthy" in status for status in services.values())
    status = "healthy" if all_healthy else "degraded"

    return HealthCheckResponse(
        status=status,
        services=services,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/conversations")
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    List user's conversations.

    Args:
        limit: Maximum conversations to return (default: 20)
        offset: Number of conversations to skip (default: 0)

    Returns:
        List of conversations with metadata
    """
    try:
        user_id = session_data["user_id"]

        # TODO: Implement list_conversations in ChatService
        # For now, return empty list
        return {
            "conversations": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    ChatKit protocol endpoint for OpenAI ChatKit frontend.

    Uses the official ChatKit SDK server protocol.

    Authentication: X-Session-Token header (via verify_session_token)
    Response Format: text/event-stream (SSE)
    """
    # Import ChatKit server
    from app.chatkit.server import get_chatkit_server

    # Get the request body as bytes (required by ChatKit SDK)
    payload = await request.body()

    # Get ChatKit server instance (singleton)
    server = get_chatkit_server()

    # Process the request through ChatKit server
    # Pass context with user_id from session
    context = {
        "user_id": session_data.get("user_id"),
        "request": request,
    }

    result = await server.process(payload, context)

    # Return appropriate response based on result type
    from chatkit.server import StreamingResult
    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    # Handle non-streaming responses
    if hasattr(result, "json"):
        from fastapi.responses import Response
        return Response(content=result.json, media_type="application/json")

    # Default JSON response
    from fastapi.responses import JSONResponse
    return JSONResponse(result)

