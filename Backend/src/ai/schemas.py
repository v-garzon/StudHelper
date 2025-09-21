"""AI schemas."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field


class ChatMode(str, Enum):
    """Chat mode enumeration."""
    ECONOMIC = "economic"
    STANDARD = "standard"
    TURBO = "turbo"


class ChatMessageRequest(BaseModel):
    """Chat message request schema."""
    message: str = Field(..., min_length=1, max_length=5000)
    mode: ChatMode = ChatMode.ECONOMIC
    session_id: Optional[int] = None
    include_context: bool = True
    max_context_length: int = Field(4000, ge=1000, le=8000)


class ChatMessageResponse(BaseModel):
    """Chat message response schema."""
    content: str
    role: str = "assistant"
    mode: str
    model: str
    session_id: int
    
    # Usage information
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    
    # Context information
    context_used: bool
    sources: List[Dict[str, Any]]
    
    # Metadata
    response_time: float
    timestamp: datetime


class ChatSessionResponse(BaseModel):
    """Chat session response schema."""
    id: int
    title: Optional[str]
    mode: str
    message_count: int
    total_tokens: int
    total_cost: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StreamingChunk(BaseModel):
    """Streaming response chunk."""
    delta: str
    session_id: Optional[int] = None
    finished: bool = False
    
    # Final usage info (only when finished=True)
    usage: Optional[Dict[str, int]] = None
    cost: Optional[float] = None


class MessageFeedback(BaseModel):
    """Message feedback schema."""
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

