from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import ProcessingStatus, DocumentScope

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

# Class schemas
class ClassBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassResponse(ClassBase):
    id: int
    class_code: str
    owner_id: int
    created_at: datetime
    is_active: bool
    member_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class JoinClassRequest(BaseModel):
    class_code: str

# Permission schemas
class PermissionUpdate(BaseModel):
    can_read: Optional[bool] = None
    can_chat: Optional[bool] = None
    max_concurrent_chats: Optional[int] = None
    can_share_class: Optional[bool] = None
    can_upload_documents: Optional[bool] = None
    daily_token_limit: Optional[int] = None
    weekly_token_limit: Optional[int] = None
    monthly_token_limit: Optional[int] = None

class MembershipResponse(BaseModel):
    id: int
    user_id: int
    username: str
    full_name: Optional[str]
    joined_at: datetime
    is_manager: bool
    can_read: bool
    can_chat: bool
    max_concurrent_chats: int
    can_share_class: bool
    can_upload_documents: bool
    is_sponsored: bool
    daily_token_limit: int
    weekly_token_limit: int
    monthly_token_limit: int
    
    class Config:
        from_attributes = True

class SponsorshipUpdate(BaseModel):
    is_sponsored: bool

# Document schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    scope: DocumentScope
    class_id: int
    session_id: Optional[int]
    uploaded_by: int
    uploaded_at: datetime
    processing_status: ProcessingStatus
    processing_error: Optional[str]
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatSessionCreate(BaseModel):
    title: str
    class_id: int

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    user_id: int
    class_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    session_id: int
    content: str
    is_user: bool
    timestamp: datetime
    response_time_ms: Optional[int]
    context_used: Optional[str]
    tokens_used: int
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    user_message: MessageResponse
    ai_response: MessageResponse
    cost: float
    response_time_ms: int
    context_provided: bool

# Usage schemas
class UsageStats(BaseModel):
    daily_tokens_used: int
    weekly_tokens_used: int
    monthly_tokens_used: int
    daily_limit: int
    weekly_limit: int
    monthly_limit: int
    daily_remaining: int
    weekly_remaining: int
    monthly_remaining: int

class ClassUsageOverview(BaseModel):
    user_id: int
    username: str
    usage_stats: UsageStats
    is_sponsored: bool
    last_activity: Optional[datetime]

class UsageRecord(BaseModel):
    id: int
    model_name: str
    operation_type: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: datetime
    is_sponsored: bool
    is_overflow: bool

