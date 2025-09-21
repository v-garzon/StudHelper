"""AI chat routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db_session
from src.core.deps import get_default_user
from src.ai.schemas import ChatMessageRequest, ChatMessageResponse, MessageFeedback
from src.ai.service import ChatService
from src.usage.tracker import UsageTracker

router = APIRouter()


@router.post("/chat", response_model=ChatMessageResponse)
async def chat(
    request: ChatMessageRequest,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Send a chat message."""
    # Check usage limits
    usage_tracker = UsageTracker()
    limits = await usage_tracker.check_user_limits(user.id)
    
    if not limits["within_limits"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily usage limit exceeded",
        )
    
    chat_service = ChatService(db)
    return await chat_service.chat(request, user.id)


@router.post("/chat/stream")
async def stream_chat(
    request: ChatMessageRequest,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Send a chat message with streaming response."""
    # Check usage limits
    usage_tracker = UsageTracker()
    limits = await usage_tracker.check_user_limits(user.id)
    
    if not limits["within_limits"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily usage limit exceeded",
        )
    
    chat_service = ChatService(db)
    
    async def generate():
        async for chunk in chat_service.stream_chat(request, user.id):
            yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/sessions")
async def get_chat_sessions(
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get user's chat sessions."""
    chat_service = ChatService(db)
    return await chat_service.get_chat_sessions(user.id)


@router.get("/sessions/{session_id}/history")
async def get_chat_history(
    session_id: int,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get chat history for a session."""
    chat_service = ChatService(db)
    return await chat_service.get_chat_history(session_id, user.id)


@router.post("/messages/{message_id}/feedback")
async def submit_feedback(
    message_id: int,
    feedback: MessageFeedback,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Submit feedback for a message."""
    # Implementation would update the ChatMessage with feedback
    return {"message": "Feedback submitted successfully"}


