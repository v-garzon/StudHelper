"""Usage tracking models."""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import DateTime, Date, ForeignKey, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class UsageLog(Base):
    """Usage log model for detailed tracking."""
    
    __tablename__ = "usage_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    # API usage details
    endpoint: Mapped[str] = mapped_column(String(100))  # chat, documents, etc.
    model: Mapped[str] = mapped_column(String(100))
    
    # Token usage
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    total_tokens: Mapped[int] = mapped_column(Integer)
    
    # Cost
    cost: Mapped[float] = mapped_column(Float)
    
    # Session info
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserQuota(Base):
    """User daily quotas and limits."""
    
    __tablename__ = "user_quotas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, index=True)
    
    # Daily usage
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_incurred: Mapped[float] = mapped_column(Float, default=0.0)
    requests_made: Mapped[int] = mapped_column(Integer, default=0)
    
    # Daily limits
    daily_token_limit: Mapped[int] = mapped_column(Integer, default=10000)
    daily_cost_limit: Mapped[float] = mapped_column(Float, default=1.00)
    daily_request_limit: Mapped[int] = mapped_column(Integer, default=100)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

