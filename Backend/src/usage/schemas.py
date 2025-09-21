"""Usage tracking schemas."""

from datetime import datetime, date
from typing import Dict, List, Any, Optional

from pydantic import BaseModel


class UsageLogResponse(BaseModel):
    """Usage log response schema."""
    id: int
    endpoint: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class DailyUsage(BaseModel):
    """Daily usage summary."""
    date: date
    tokens_used: int
    cost_incurred: float
    requests_made: int
    tokens_remaining: int
    cost_remaining: float
    requests_remaining: int
    within_limits: bool


class UsageAnalytics(BaseModel):
    """Usage analytics response."""
    period_days: int
    total_tokens: int
    total_cost: float
    total_requests: int
    avg_tokens_per_request: float
    avg_cost_per_request: float
    usage_by_model: List[Dict[str, Any]]
    usage_by_endpoint: List[Dict[str, Any]]
    daily_breakdown: List[DailyUsage]


class QuotaUpdate(BaseModel):
    """Quota update request."""
    daily_token_limit: Optional[int] = None
    daily_cost_limit: Optional[float] = None
    daily_request_limit: Optional[int] = None

