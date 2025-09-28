from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import ChatSessionCreate, ChatSessionResponse, MessageCreate, MessageResponse, ChatResponse, UserResponse
from app.services.permission_service import PermissionService
from app.services.chat_service import ChatService
from app.utils.security import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    try:
        permission_service = PermissionService()
        
        # Check if user can chat in this class
        can_chat, reason = await permission_service.can_user_chat(db, current_user.id, session_data.class_id)
        if not can_chat:
            if "limit reached" in reason.lower():
                raise HTTPException(status_code=429, detail=reason)
            else:
                raise HTTPException(status_code=403, detail=reason)
        
        chat_service = ChatService()
        session = await chat_service.create_session(db, current_user.id, session_data)
        
        logger.info(f"Chat session created: {session.title} by {current_user.username}")
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions"""
    try:
        from app.models import ChatSession, ChatMessage
        
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).order_by(ChatSession.updated_at.desc()).all()
        
        result = []
        for session in sessions:
            # Count messages
            message_count = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).count()
            
            session_response = ChatSessionResponse.model_validate(session)
            session_response.message_count = message_count
            result.append(session_response)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session_details(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat session details"""
    try:
        from app.models import ChatSession, ChatMessage
        
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Count messages
        message_count = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).count()
        
        result = ChatSessionResponse.model_validate(session)
        result.message_count = message_count
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: int,
    message_data: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    try:
        from app.models import ChatSession
        
        # Get session and verify ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Check permissions
        permission_service = PermissionService()
        can_chat, reason = await permission_service.can_user_chat(db, current_user.id, session.class_id)
        if not can_chat:
            if "limit reached" in reason.lower():
                raise HTTPException(status_code=429, detail=reason)
            else:
                raise HTTPException(status_code=403, detail=reason)
        
        # Send message and get AI response
        chat_service = ChatService()
        chat_response = await chat_service.send_message(db, session, message_data.content, current_user.id)
        
        logger.info(f"Message sent in session {session_id} by {current_user.username}")
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get messages from a chat session"""
    try:
        from app.models import ChatSession, ChatMessage
        
        # Verify session ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get messages
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.asc()).offset(offset).limit(limit).all()
        
        return [MessageResponse.model_validate(msg) for msg in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

