from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Tuple, Optional
from app.models import ClassMembership, ClassUsageTracker, ChatSession
import pytz
import logging

logger = logging.getLogger(__name__)

class PermissionService:
    
    async def get_user_membership(self, db: Session, user_id: int, class_id: int) -> Optional[ClassMembership]:
        """Get user's membership in a specific class"""
        return db.query(ClassMembership).filter(
            ClassMembership.user_id == user_id,
            ClassMembership.class_id == class_id
        ).first()
    
    async def can_user_chat(self, db: Session, user_id: int, class_id: int) -> Tuple[bool, str]:
        """Check if user can chat in this class"""
        membership = await self.get_user_membership(db, user_id, class_id)
        
        if not membership:
            return False, "User not enrolled in this class"
        
        if not membership.can_chat:
            return False, "Chat permission disabled by class manager"
        
        # Check token limits
        usage_check = await self.check_token_limits(db, user_id, class_id, membership)
        if not usage_check[0]:
            return usage_check
        
        # Check concurrent chat limit
        active_chats = await self.count_active_chats(db, user_id, class_id)
        if active_chats >= membership.max_concurrent_chats:
            return False, f"Maximum concurrent chats reached ({membership.max_concurrent_chats}). Please close some chats first."
        
        return True, "OK"
    
    async def check_token_limits(self, db: Session, user_id: int, class_id: int, membership: ClassMembership) -> Tuple[bool, str]:
        """Check if user is within token limits"""
        # Get or create usage tracker
        tracker = await self.get_usage_tracker(db, user_id, class_id)
        
        # Reset counters if needed
        await self.reset_usage_if_needed(db, tracker)
        
        # Check limits
        if tracker.daily_tokens_used >= membership.daily_token_limit:
            return False, "Daily token limit reached. Upgrade to continue chatting or wait for daily reset."
        
        if tracker.weekly_tokens_used >= membership.weekly_token_limit:
            return False, "Weekly token limit reached. Upgrade to continue chatting or wait for weekly reset."
        
        if tracker.monthly_tokens_used >= membership.monthly_token_limit:
            return False, "Monthly token limit reached. Upgrade to continue chatting or wait for monthly reset."
        
        return True, "OK"
    
    async def get_usage_tracker(self, db: Session, user_id: int, class_id: int) -> ClassUsageTracker:
        """Get or create usage tracker for user in class"""
        tracker = db.query(ClassUsageTracker).filter(
            ClassUsageTracker.user_id == user_id,
            ClassUsageTracker.class_id == class_id
        ).first()
        
        if not tracker:
            tracker = ClassUsageTracker(
                user_id=user_id,
                class_id=class_id,
                last_daily_reset=date.today(),
                last_weekly_reset=date.today(),
                last_monthly_reset=date.today()
            )
            db.add(tracker)
            db.commit()
            db.refresh(tracker)
        
        return tracker
    
    async def reset_usage_if_needed(self, db: Session, tracker: ClassUsageTracker):
        """Reset usage counters based on Madrid timezone (00:00)"""
        madrid_tz = pytz.timezone('Europe/Madrid')
        today = date.today()
        
        reset_needed = False
        
        # Daily reset
        if tracker.last_daily_reset != today:
            tracker.daily_tokens_used = 0
            tracker.last_daily_reset = today
            reset_needed = True
        
        # Weekly reset (every Monday)
        if self.is_new_week(tracker.last_weekly_reset, today):
            tracker.weekly_tokens_used = 0
            tracker.last_weekly_reset = today
            reset_needed = True
        
        # Monthly reset (1st of month)
        if self.is_new_month(tracker.last_monthly_reset, today):
            tracker.monthly_tokens_used = 0
            tracker.last_monthly_reset = today
            reset_needed = True
        
        if reset_needed:
            db.commit()
    
    def is_new_week(self, last_reset: date, today: date) -> bool:
        """Check if we've entered a new week (Monday start)"""
        # Get Monday of last reset week
        last_monday = last_reset - timedelta(days=last_reset.weekday())
        # Get Monday of current week
        current_monday = today - timedelta(days=today.weekday())
        return current_monday > last_monday
    
    def is_new_month(self, last_reset: date, today: date) -> bool:
        """Check if we've entered a new month"""
        return (today.year, today.month) != (last_reset.year, last_reset.month)
    
    async def count_active_chats(self, db: Session, user_id: int, class_id: int) -> int:
        """Count active chat sessions for user in class"""
        return db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.class_id == class_id,
            ChatSession.is_active == True
        ).count()
    
    async def determine_billing(self, db: Session, user_id: int, class_id: int) -> Tuple[int, bool, bool]:
        """
        Determine billing for usage
        Returns: (billed_user_id, is_sponsored, is_overflow)
        """
        membership = await self.get_user_membership(db, user_id, class_id)
        
        if membership and membership.is_sponsored:
            # Find class owner (manager who sponsors)
            from app.models import Class
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            return class_obj.owner_id, True, False  # Manager pays, sponsored, not overflow
        else:
            return user_id, False, True  # User pays, not sponsored, is overflow
    
    async def record_token_usage(self, db: Session, user_id: int, class_id: int, tokens_used: int):
        """Record token usage in the tracker"""
        tracker = await self.get_usage_tracker(db, user_id, class_id)
        await self.reset_usage_if_needed(db, tracker)
        
        tracker.daily_tokens_used += tokens_used
        tracker.weekly_tokens_used += tokens_used
        tracker.monthly_tokens_used += tokens_used
        
        db.commit()

