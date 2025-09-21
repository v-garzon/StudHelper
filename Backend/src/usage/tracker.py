"""Usage tracking service."""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.usage.models import UsageLog, UserQuota
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class UsageTracker:
    """Usage tracking service."""
    
    async def track_usage(
        self,
        user_id: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        endpoint: str = "chat",
        session_id: Optional[str] = None,
    ) -> bool:
        """Track API usage and update user quotas."""
        async with get_db() as db:
            try:
                # Log detailed usage
                usage_log = UsageLog(
                    user_id=user_id,
                    endpoint=endpoint,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    cost=cost,
                    session_id=session_id,
                    timestamp=datetime.utcnow(),
                )
                
                db.add(usage_log)
                
                # Update user's daily usage
                await self._update_daily_usage(
                    db=db,
                    user_id=user_id,
                    tokens=input_tokens + output_tokens,
                    cost=cost,
                    requests=1,
                )
                
                await db.commit()
                logger.info(f"Tracked usage for user {user_id}: {input_tokens + output_tokens} tokens, ${cost:.4f}")
                return True
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Usage tracking error: {str(e)}")
                return False
    
    async def _update_daily_usage(
        self,
        db: AsyncSession,
        user_id: int,
        tokens: int,
        cost: float,
        requests: int,
    ):
        """Update user's daily usage totals."""
        today = datetime.utcnow().date()
        
        # Get or create daily quota record
        result = await db.execute(
            select(UserQuota).where(
                and_(
                    UserQuota.user_id == user_id,
                    UserQuota.date == today,
                )
            )
        )
        
        quota = result.scalar_one_or_none()
        
        if quota:
            quota.tokens_used += tokens
            quota.cost_incurred += cost
            quota.requests_made += requests
        else:
            quota = UserQuota(
                user_id=user_id,
                date=today,
                tokens_used=tokens,
                cost_incurred=cost,
                requests_made=requests,
                daily_token_limit=10000,  # Default limit
                daily_cost_limit=1.00,   # Default $1/day limit
                daily_request_limit=100, # Default request limit
            )
            db.add(quota)
    
    async def check_user_limits(self, user_id: int) -> Dict[str, Any]:
        """Check if user has exceeded daily limits."""
        async with get_db() as db:
            today = datetime.utcnow().date()
            
            result = await db.execute(
                select(UserQuota).where(
                    and_(
                        UserQuota.user_id == user_id,
                        UserQuota.date == today,
                    )
                )
            )
            
            quota = result.scalar_one_or_none()
            
            if not quota:
                return {
                    "within_limits": True,
                    "tokens_used": 0,
                    "cost_incurred": 0.0,
                    "requests_made": 0,
                    "tokens_remaining": 10000,
                    "cost_remaining": 1.00,
                    "requests_remaining": 100,
                }
            
            tokens_exceeded = quota.tokens_used >= quota.daily_token_limit
            cost_exceeded = quota.cost_incurred >= quota.daily_cost_limit
            requests_exceeded = quota.requests_made >= quota.daily_request_limit
            
            return {
                "within_limits": not (tokens_exceeded or cost_exceeded or requests_exceeded),
                "tokens_used": quota.tokens_used,
                "tokens_limit": quota.daily_token_limit,
                "tokens_exceeded": tokens_exceeded,
                "cost_incurred": quota.cost_incurred,
                "cost_limit": quota.daily_cost_limit,
                "cost_exceeded": cost_exceeded,
                "requests_made": quota.requests_made,
                "requests_limit": quota.daily_request_limit,
                "requests_exceeded": requests_exceeded,
                "tokens_remaining": max(0, quota.daily_token_limit - quota.tokens_used),
                "cost_remaining": max(0.0, quota.daily_cost_limit - quota.cost_incurred),
                "requests_remaining": max(0, quota.daily_request_limit - quota.requests_made),
            }
    
    async def get_usage_analytics(
        self,
        user_id: int,
        days_back: int = 30,
    ) -> Dict[str, Any]:
        """Get usage analytics for a user."""
        async with get_db() as db:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get total usage over period
            result = await db.execute(
                select(
                    func.sum(UsageLog.total_tokens).label('total_tokens'),
                    func.sum(UsageLog.cost).label('total_cost'),
                    func.count(UsageLog.id).label('request_count'),
                    func.avg(UsageLog.total_tokens).label('avg_tokens_per_request'),
                    func.avg(UsageLog.cost).label('avg_cost_per_request'),
                ).where(
                    and_(
                        UsageLog.user_id == user_id,
                        UsageLog.timestamp >= start_date,
                    )
                )
            )
            
            stats = result.one()
            
            # Get usage by model
            model_usage = await db.execute(
                select(
                    UsageLog.model,
                    func.sum(UsageLog.total_tokens).label('tokens'),
                    func.sum(UsageLog.cost).label('cost'),
                    func.count(UsageLog.id).label('requests'),
                ).where(
                    and_(
                        UsageLog.user_id == user_id,
                        UsageLog.timestamp >= start_date,
                    )
                ).group_by(UsageLog.model)
            )
            
            # Get usage by endpoint
            endpoint_usage = await db.execute(
                select(
                    UsageLog.endpoint,
                    func.sum(UsageLog.total_tokens).label('tokens'),
                    func.sum(UsageLog.cost).label('cost'),
                    func.count(UsageLog.id).label('requests'),
                ).where(
                    and_(
                        UsageLog.user_id == user_id,
                        UsageLog.timestamp >= start_date,
                    )
                ).group_by(UsageLog.endpoint)
            )
            
            # Get daily breakdown
            daily_usage = await db.execute(
                select(UserQuota).where(
                    and_(
                        UserQuota.user_id == user_id,
                        UserQuota.date >= start_date.date(),
                    )
                ).order_by(UserQuota.date.desc())
            )
            
            return {
                "period_days": days_back,
                "total_tokens": int(stats.total_tokens or 0),
                "total_cost": float(stats.total_cost or 0),
                "total_requests": int(stats.request_count or 0),
                "avg_tokens_per_request": float(stats.avg_tokens_per_request or 0),
                "avg_cost_per_request": float(stats.avg_cost_per_request or 0),
                "usage_by_model": [
                    {
                        "model": row.model,
                        "tokens": int(row.tokens),
                        "cost": float(row.cost),
                        "requests": int(row.requests),
                    }
                    for row in model_usage
                ],
                "usage_by_endpoint": [
                    {
                        "endpoint": row.endpoint,
                        "tokens": int(row.tokens),
                        "cost": float(row.cost),
                        "requests": int(row.requests),
                    }
                    for row in endpoint_usage
                ],
                "daily_breakdown": [
                    {
                        "date": quota.date,
                        "tokens_used": quota.tokens_used,
                        "cost_incurred": quota.cost_incurred,
                        "requests_made": quota.requests_made,
                        "tokens_remaining": max(0, quota.daily_token_limit - quota.tokens_used),
                        "cost_remaining": max(0.0, quota.daily_cost_limit - quota.cost_incurred),
                        "requests_remaining": max(0, quota.daily_request_limit - quota.requests_made),
                        "within_limits": (
                            quota.tokens_used < quota.daily_token_limit and
                            quota.cost_incurred < quota.daily_cost_limit and
                            quota.requests_made < quota.daily_request_limit
                        ),
                    }
                    for quota in daily_usage.scalars().all()
                ],
            }
    
    async def update_user_quotas(
        self,
        user_id: int,
        daily_token_limit: Optional[int] = None,
        daily_cost_limit: Optional[float] = None,
        daily_request_limit: Optional[int] = None,
    ) -> bool:
        """Update user's daily quotas."""
        async with get_db() as db:
            try:
                today = datetime.utcnow().date()
                
                # Get or create quota record
                result = await db.execute(
                    select(UserQuota).where(
                        and_(
                            UserQuota.user_id == user_id,
                            UserQuota.date == today,
                        )
                    )
                )
                
                quota = result.scalar_one_or_none()
                
                if not quota:
                    quota = UserQuota(
                        user_id=user_id,
                        date=today,
                        daily_token_limit=daily_token_limit or 10000,
                        daily_cost_limit=daily_cost_limit or 1.00,
                        daily_request_limit=daily_request_limit or 100,
                    )
                    db.add(quota)
                else:
                    if daily_token_limit is not None:
                        quota.daily_token_limit = daily_token_limit
                    if daily_cost_limit is not None:
                        quota.daily_cost_limit = daily_cost_limit
                    if daily_request_limit is not None:
                        quota.daily_request_limit = daily_request_limit
                
                await db.commit()
                return True
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Error updating quotas: {str(e)}")
                return False

