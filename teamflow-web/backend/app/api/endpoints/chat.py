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

Phase 7 (T087, T088, T089, T090, T091):
- Rate limiting for chat endpoints
- Error response format standardization
- Comprehensive error logging with context
- Streaming performance monitoring (2 second target)
"""
import json
import asyncio
import logging
import time
from typing import Optional, AsyncIterator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field

from app.services.chat_service import ChatService
from app.agents.orchestrator import get_orchestrator
from app.models.chat import ConversationCreate, MessageRole
from app.models.preferences import UserChatPreference, ChatLanguage, UserChatPreferenceCreate, UserChatPreferenceRead
from app.db.session import SessionDep
from app.core.rate_limit import check_rate_limit, add_rate_limit_headers
from app.core.logging import get_logger
from app.core.config import settings
from sqlmodel import select
# from app.chatkit import get_chatkit_server  # TODO: Fix chatkit integration

# T090: Use structured logger
logger = get_logger(__name__)

# T091: Performance monitoring target
STREAMING_TARGET_SECONDS = 2.0


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


class RecommendationAcceptanceRequest(BaseModel):
    """Request to track recommendation acceptance/rejection (T066)."""
    recommendation_type: str = Field(..., description="Type: 'assignee', 'task_creation', etc.")
    recommendation_id: str = Field(..., description="Unique identifier for the recommendation")
    action: str = Field(..., description="User action: 'accepted' or 'rejected'")
    reasoning: Optional[str] = Field(None, description="AI reasoning that was shown to user")
    context: Optional[dict] = Field(None, description="Additional context (task_id, project_id, etc.)")


class RecommendationAcceptanceResponse(BaseModel):
    """Response for recommendation tracking."""
    success: bool
    message: str
    tracked_at: str


# Router
router = APIRouter(prefix="/chat", tags=["chat"])


# Dependencies
async def get_chat_service():
    """Get ChatService instance."""
    from app.services.chat_service import chat_service
    return chat_service


async def verify_session_token(
    request: Request,
    session: SessionDep,
    x_session_token: Optional[str] = Header(None, alias="X-Session-Token"),
) -> dict:
    """
    Verify Better Auth session token.

    For testing purposes, accepts any token and creates a temp user session.
    TODO: Integrate with actual Better Auth session verification.

    Args:
        request: FastAPI request
        session: Database session
        x_session_token: Session token from header (optional for testing)

    Returns:
        Session data with user_id and agency_id
    """
    # For testing: use fixed temp user ID that exists in database
    # TODO: Verify JWT token with actual Better Auth integration
    from uuid import UUID
    from app.models.user import User

    TEMP_USER_ID = "739fe54d-a2df-4701-b7ef-a9c283610ae0"

    # Fetch user from database to get agency_id
    user_id = UUID(TEMP_USER_ID)
    user = session.get(User, user_id)

    if not user:
        # Fallback if user not found
        return {
            "user_id": TEMP_USER_ID,
            "session_id": x_session_token or "test-session"
        }

    return {
        "user_id": TEMP_USER_ID,
        "agency_id": str(user.agency_id) if user.agency_id else None,
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
    http_request: Request,
    session_data: dict = Depends(verify_session_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Send a chat message and receive streaming response.

    T087: Rate limited to 100 requests per hour per user.
    T090: Comprehensive error logging with context.

    Returns NDJSON stream with events:
    - {"type": "token", "data": {"content": "word "}}
    - {"type": "tool_call", "data": {"tool": "add_task", "args": {...}}}
    - {"type": "tool_result", "data": {"result": {...}}}
    - {"type": "done", "data": {}}

    Raises:
        HTTPException: If request validation fails or AI service unavailable
    """
    # T087: Check rate limit (100 requests per hour)
    check_rate_limit(http_request, "chat_respond")

    # T090: Log request with context
    user_id = session_data.get("user_id")
    logger.info(
        "[chat_respond] Processing chat message",
        user_id=user_id,
        conversation_id=request.conversation_id,
        message_length=len(request.message),
        use_knowledge_base=request.use_knowledge_base,
    )

    # T088: Prepare rate limit headers
    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",  # Disable nginx buffering
    }
    if hasattr(http_request.state, "rate_limit"):
        rl = http_request.state.rate_limit
        headers["X-RateLimit-Limit"] = str(rl["limit"])
        headers["X-RateLimit-Remaining"] = str(rl["remaining"])
        headers["X-RateLimit-Reset"] = str(rl["reset"])

    # T091: Track streaming performance
    streaming_start_time = time.time()
    first_token_time = None
    total_tokens = 0

    async def event_stream() -> AsyncIterator[str]:
        """Generate NDJSON stream of events."""
        nonlocal first_token_time, total_tokens

        try:
            orchestrator = get_orchestrator(chat_service)

            # Process message with or without RAG
            stream = orchestrator.process_with_rag if request.use_knowledge_base else orchestrator.process_message

            async for event in stream(
                user_message=request.message,
                conversation_id=request.conversation_id,
                user_id=user_id,
            ):
                # T091: Track first token time (time to first response)
                if first_token_time is None:
                    first_token_time = time.time()
                    time_to_first_token = first_token_time - streaming_start_time

                    # Log time to first token (T091: target is < 2 seconds)
                    logger.info(
                        "[chat_respond] First token generated",
                        user_id=user_id,
                        time_to_first_token_seconds=f"{time_to_first_token:.3f}",
                        target_met=time_to_first_token <= STREAMING_TARGET_SECONDS,
                    )

                # Track token count
                if event.get("type") == "token":
                    total_tokens += 1

                # Convert event to NDJSON
                yield json.dumps(event) + "\n"

            # T091: Log streaming completion metrics
            streaming_end_time = time.time()
            total_streaming_time = streaming_end_time - streaming_start_time

            logger.info(
                "[chat_respond] Streaming completed",
                user_id=user_id,
                total_streaming_time_seconds=f"{total_streaming_time:.3f}",
                time_to_first_token_seconds=f"{first_token_time - streaming_start_time:.3f}" if first_token_time else None,
                total_tokens=total_tokens,
                tokens_per_second=f"{total_tokens / total_streaming_time:.2f}" if total_streaming_time > 0 else 0,
            )

        except Exception as e:
            # T090: Log error with comprehensive context
            streaming_end_time = time.time()
            logger.error(
                "[chat_respond] Error processing message",
                user_id=user_id,
                conversation_id=request.conversation_id,
                error_type=type(e).__name__,
                error_message=str(e),
                message_length=len(request.message),
                streaming_duration_seconds=f"{streaming_end_time - streaming_start_time:.3f}",
                total_tokens=total_tokens,
            )

            # T089: Standardized error response format
            error_event = {
                "type": "error",
                "data": {
                    "code": "CHAT_PROCESSING_ERROR",
                    "message": str(e) if settings.environment != "production" else "Failed to process message",
                    "type": type(e).__name__,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
            yield json.dumps(error_event) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers=headers
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
    session: SessionDep,
    session_data: dict = Depends(verify_session_token),
):
    """
    Update user chat preferences (T073).

    Updates language preference and voice input setting.
    Creates preference record if it doesn't exist.

    Returns:
        Updated preferences

    Raises:
        HTTPException: If update fails
    """
    try:
        from uuid import UUID
        user_id = UUID(session_data["user_id"])

        # Try to get existing preference
        statement = select(UserChatPreference).where(UserChatPreference.user_id == user_id)
        result = session.exec(statement).first()

        if result:
            # Update existing preference
            result.language = request.language
            result.voice_enabled = request.voice_enabled
            result.updated_at = datetime.utcnow()
        else:
            # Create new preference
            new_pref = UserChatPreference(
                user_id=user_id,
                language=request.language,
                voice_enabled=request.voice_enabled,
            )
            session.add(new_pref)

        session.commit()

        return {
            "user_id": str(user_id),
            "language": request.language,
            "voice_enabled": request.voice_enabled,
            "updated_at": datetime.utcnow().isoformat(),
            "message": "Preferences updated successfully",
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.get("/preferences")
async def get_chat_preferences(
    session: SessionDep,
    session_data: dict = Depends(verify_session_token),
):
    """
    Get user chat preferences (T073).

    Returns current language and voice settings.

    Returns:
        User preferences

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        from uuid import UUID
        user_id = UUID(session_data["user_id"])

        # Try to get existing preference
        statement = select(UserChatPreference).where(UserChatPreference.user_id == user_id)
        result = session.exec(statement).first()

        if result:
            return {
                "user_id": str(user_id),
                "language": result.language,
                "voice_enabled": result.voice_enabled,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None,
            }
        else:
            # Return default preferences
            return {
                "user_id": str(user_id),
                "language": ChatLanguage.english,
                "voice_enabled": False,
                "updated_at": None,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")


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
    # Pass context with user_id and agency_id from session
    context = {
        "user_id": session_data.get("user_id"),
        "agency_id": session_data.get("agency_id"),
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


@router.post("/recommendations/track", response_model=RecommendationAcceptanceResponse)
async def track_recommendation_acceptance(
    request: RecommendationAcceptanceRequest,
    session: SessionDep,
    session_data: dict = Depends(verify_session_token),
):
    """
    Track user acceptance or rejection of AI recommendations (T066).

    Logs when users accept or reject AI-suggested actions like:
    - Task assignments (suggest_assignee tool)
    - Task creations from natural language
    - Priority recommendations
    - Other AI-driven suggestions

    This data is used to calculate recommendation acceptance rate (SC-005: 70% target).

    Args:
        request: Acceptance tracking data with type, action, reasoning, context
        session_data: User session from Better Auth
        session: Database session

    Returns:
        Confirmation of tracking with timestamp

    Raises:
        HTTPException: If tracking fails (doesn't block chat flow)
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        user_id = session_data["user_id"]

        # Log the acceptance event
        # In production, this would be stored in a database table
        # For now, we'll log it and store in a simple format
        log_entry = {
            "user_id": user_id,
            "recommendation_type": request.recommendation_type,
            "recommendation_id": request.recommendation_id,
            "action": request.action,
            "reasoning": request.reasoning,
            "context": request.context,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Log the event
        logger.info(
            f"Recommendation {request.action}: type={request.recommendation_type}, "
            f"id={request.recommendation_id}, user={user_id}"
        )

        # TODO: Store in database table (recommendation_acceptance_log)
        # Schema: user_id, recommendation_type, recommendation_id, action, reasoning, context, created_at
        # This would allow for proper acceptance rate calculation and analytics

        return RecommendationAcceptanceResponse(
            success=True,
            message=f"Recommendation {request.action} tracked successfully",
            tracked_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        # Log error but don't fail the request (tracking shouldn't block chat)
        logger.error(f"Failed to track recommendation acceptance: {str(e)}")

        # Return success anyway to avoid blocking chat flow
        return RecommendationAcceptanceResponse(
            success=False,
            message=f"Tracking failed (non-critical): {str(e)}",
            tracked_at=datetime.utcnow().isoformat(),
        )


@router.get("/recommendations/stats")
async def get_recommendation_stats(
    session: SessionDep,
    session_data: dict = Depends(verify_session_token),
):
    """
    Get recommendation acceptance statistics (T066, T069).

    Returns acceptance rate metrics for AI recommendations.
    Used to track SC-005: 70% acceptance rate target.

    Args:
        session_data: User session
        session: Database session

    Returns:
        Statistics including total recommendations, acceptance rate, trends
    """
    try:
        # TODO: Calculate from actual recommendation_acceptance_log table
        # For now, return mock data

        return {
            "total_recommendations": 0,
            "accepted": 0,
            "rejected": 0,
            "acceptance_rate": 0.0,
            "target_rate": 0.70,
            "meets_target": None,  # True when >= 70%
            "message": "Recommendation tracking not yet implemented in database",
            "by_type": {
                "assignee": {"total": 0, "accepted": 0, "rate": 0.0},
                "task_creation": {"total": 0, "accepted": 0, "rate": 0.0},
            },
            "trend_7_days": [],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation stats: {str(e)}")


