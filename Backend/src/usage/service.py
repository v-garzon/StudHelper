"""Usage service."""

import logging
from typing import Dict, List, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.usage.tracker import UsageTracker
from src.usage.schemas import UsageAnalytics, DailyUsage, QuotaUpdate

logger = logging.getLogger(__name__)


class UsageService:
    """Usage service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tracker = UsageTracker()
    
    async def get_user_analytics(self, user_id: int, days: int = 30) -> UsageAnalytics:
        """Get comprehensive usage analytics."""
        data = await self.tracker.get_usage_analytics(user_id, days)
        
        return UsageAnalytics(
            period_days=data["period_days"],
            total_tokens=data["total_tokens"],
            total_cost=data["total_cost"],
            total_requests=data["total_requests"],
            avg_tokens_per_request=data["avg_tokens_per_request"],
            avg_cost_per_request=data["avg_cost_per_request"],
            usage_by_model=data["usage_by_model"],
            usage_by_endpoint=data["usage_by_endpoint"],
            daily_breakdown=[
                DailyUsage(**daily) for daily in data["daily_breakdown"]
            ],
        )
    
    async def get_current_limits(self, user_id: int) -> Dict[str, Any]:
        """Get current usage limits and status."""
        return await self.tracker.check_user_limits(user_id)
    
    async def update_quotas(self, user_id: int, quota_update: QuotaUpdate) -> bool:
        """Update user quotas."""
        return await self.tracker.update_user_quotas(
            user_id=user_id,
            daily_token_limit=quota_update.daily_token_limit,
            daily_cost_limit=quota_update.daily_cost_limit,
            daily_request_limit=quota_update.daily_request_limit,
        )

