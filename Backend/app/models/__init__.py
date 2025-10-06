from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from sqlalchemy import Enum

Base = declarative_base()

class ProcessingStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentScope(enum.Enum):
    CLASS = "class"    # Available to all chats in the class
    CHAT = "chat"      # Only available to specific chat session

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # NEW: Name fields replacing username/full_name
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    alias = Column(String, nullable=True)  # Optional display name
    
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Firebase authentication fields
    firebase_uid = Column(String, unique=True, nullable=True, index=True)
    auth_provider = Column(String, default='email')
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    owned_classes = relationship("Class", back_populates="owner")
    class_memberships = relationship("ClassMembership", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    usage_records = relationship("UsageRecord", back_populates="user", foreign_keys="UsageRecord.user_id")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    class_code = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    owner = relationship("User", back_populates="owned_classes")
    memberships = relationship("ClassMembership", back_populates="class_obj")
    documents = relationship("Document", back_populates="class_obj")
    chat_sessions = relationship("ChatSession", back_populates="class_obj")

class ClassMembership(Base):
    """Class membership with granular permissions"""
    __tablename__ = "class_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Permission flags
    is_manager = Column(Boolean, default=False)
    can_read = Column(Boolean, default=True)
    can_chat = Column(Boolean, default=True)
    max_concurrent_chats = Column(Integer, default=3)
    can_share_class = Column(Boolean, default=False)
    can_upload_documents = Column(Boolean, default=True)
    
    # Billing and limits
    is_sponsored = Column(Boolean, default=False)
    daily_token_limit = Column(Integer, default=1_000_000)
    weekly_token_limit = Column(Integer, default=5_000_000)
    monthly_token_limit = Column(Integer, default=15_000_000)
    
    # Relationships
    user = relationship("User", back_populates="class_memberships")
    class_obj = relationship("Class", back_populates="memberships")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'class_id', name='_user_class_membership_uc'),
    )

class ClassUsageTracker(Base):
    """Per-class, per-user usage tracking"""
    __tablename__ = "class_usage_trackers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # Current usage counters
    daily_tokens_used = Column(Integer, default=0)
    weekly_tokens_used = Column(Integer, default=0)
    monthly_tokens_used = Column(Integer, default=0)
    
    # Reset tracking (Madrid timezone)
    last_daily_reset = Column(Date, default=date.today)
    last_weekly_reset = Column(Date, default=date.today)
    last_monthly_reset = Column(Date, default=date.today)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'class_id', name='_user_class_usage_uc'),
    )

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Dual-level document system
    scope = Column(Enum(DocumentScope), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_error = Column(Text, nullable=True)
    
    # Relationships
    class_obj = relationship("Class", back_populates="documents")
    session = relationship("ChatSession", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)
    vector_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    class_obj = relationship("Class", back_populates="chat_sessions")
    documents = relationship("Document", back_populates="session")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer, nullable=True)
    context_used = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_name = Column(String, nullable=False)
    operation_type = Column(String, nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    
    # Billing attribution
    billed_to_user_id = Column(Integer, ForeignKey("users.id"))
    is_sponsored = Column(Boolean, default=False)
    is_overflow = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="usage_records", foreign_keys=[user_id])


