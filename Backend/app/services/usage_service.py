from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models import ClassUsageTracker, ClassMembership, User, UsageRecord, ChatMessage
from app.schemas import UsageStats, ClassUsageOverview
from app.services.permission_service import PermissionService
import logging

logger = logging.getLogger(__name__)

class UsageService:
    def __init__(self):
        self.permission_service = PermissionService()
    
    async def get_user_usage_by_class(self, db: Session, user_id: int) -> List[UsageStats]:
        """Get user's usage statistics for all classes they're in"""
        try:
            # Get all user's memberships
            memberships = db.query(ClassMembership).filter(
                ClassMembership.user_id == user_id
            ).all()
            
            usage_stats = []
            
            for membership in memberships:
                stats = await self.get_user_class_usage(db, user_id, membership.class_id)
                usage_stats.append(stats)
            
            return usage_stats
            
        except Exception as e:
            logger.error(f"Error getting user usage by class: {e}")
            return []
    
    async def get_user_class_usage(self, db: Session, user_id: int, class_id: int) -> UsageStats:
        """Get user's usage statistics for a specific class"""
        try:
            # Get or create usage tracker
            tracker = await self.permission_service.get_usage_tracker(db, user_id, class_id)
            await self.permission_service.reset_usage_if_needed(db, tracker)
            
            # Get membership for limits
            membership = await self.permission_service.get_user_membership(db, user_id, class_id)
            
            if not membership:
                raise ValueError("User not found in class")
            
            return UsageStats(
                daily_tokens_used=tracker.daily_tokens_used,
                weekly_tokens_used=tracker.weekly_tokens_used,
                monthly_tokens_used=tracker.monthly_tokens_used,
                daily_limit=membership.daily_token_limit,
                weekly_limit=membership.weekly_token_limit,
                monthly_limit=membership.monthly_token_limit,
                daily_remaining=max(0, membership.daily_token_limit - tracker.daily_tokens_used),
                weekly_remaining=max(0, membership.weekly_token_limit - tracker.weekly_tokens_used),
                monthly_remaining=max(0, membership.monthly_token_limit - tracker.monthly_tokens_used)
            )
            
        except Exception as e:
            logger.error(f"Error getting user class usage: {e}")
            # Return default stats if error
            return UsageStats(
                daily_tokens_used=0,
                weekly_tokens_used=0,
                monthly_tokens_used=0,
                daily_limit=1_000_000,
                weekly_limit=5_000_000,
                monthly_limit=15_000_000,
                daily_remaining=1_000_000,
                weekly_remaining=5_000_000,
                monthly_remaining=15_000_000
            )
    
    async def get_class_usage_overview(self, db: Session, class_id: int) -> List[ClassUsageOverview]:
        """Get usage overview for all members of a class"""
        try:
            # Get all class memberships
            memberships = db.query(ClassMembership).join(User).filter(
                ClassMembership.class_id == class_id
            ).all()
            
            overview = []
            
            for membership in memberships:
                # Get usage stats for this member
                usage_stats = await self.get_user_class_usage(
                    db, membership.user_id, class_id
                )
                
                # Get last activity
                last_activity = db.query(ChatMessage.timestamp).join(
                    ChatMessage.session
                ).filter(
                    ChatMessage.session.has(user_id=membership.user_id, class_id=class_id)
                ).order_by(ChatMessage.timestamp.desc()).first()
                
                member_overview = ClassUsageOverview(
                    user_id=membership.user_id,
                    username=membership.user.username,
                    usage_stats=usage_stats,
                    is_sponsored=membership.is_sponsored,
                    last_activity=last_activity[0] if last_activity else None
                )
                
                overview.append(member_overview)
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting class usage overview: {e}")
            return []

