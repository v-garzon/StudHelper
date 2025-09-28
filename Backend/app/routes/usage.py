from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import UsageStats, ClassUsageOverview, UsageRecord, UserResponse
from app.services.usage_service import UsageService
from app.services.permission_service import PermissionService
from app.utils.security import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/my-usage", response_model=List[UsageStats])
async def get_my_usage(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage statistics across all classes"""
    try:
        usage_service = UsageService()
        usage_stats = await usage_service.get_user_usage_by_class(db, current_user.id)
        return usage_stats
        
    except Exception as e:
        logger.error(f"Error getting user usage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/classes/{class_id}/members", response_model=List[ClassUsageOverview])
async def get_class_usage_overview(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage overview for all members of a class (managers only)"""
    try:
        permission_service = PermissionService()
        
        # Check if user is manager of this class
        membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not membership or not membership.is_manager:
            raise HTTPException(status_code=403, detail="Only class managers can view usage statistics")
        
        usage_service = UsageService()
        usage_overview = await usage_service.get_class_usage_overview(db, class_id)
        return usage_overview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class usage overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/classes/{class_id}/limits")
async def get_class_limits(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's limits and usage for a specific class"""
    try:
        permission_service = PermissionService()
        usage_service = UsageService()
        
        # Check if user is member of this class
        membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get usage statistics
        usage_stats = await usage_service.get_user_class_usage(db, current_user.id, class_id)
        return usage_stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class limits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/classes/{class_id}/limits/{user_id}")
async def update_user_limits(
    class_id: int,
    user_id: int,
    daily_limit: int,
    weekly_limit: int,
    monthly_limit: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update token limits for a specific user in a class (managers only)"""
    try:
        permission_service = PermissionService()
        
        # Check if current user is manager of this class
        membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not membership or not membership.is_manager:
            raise HTTPException(status_code=403, detail="Only class managers can update limits")
        
        # Validate limits
        if daily_limit <= 0 or weekly_limit <= 0 or monthly_limit <= 0:
            raise HTTPException(status_code=400, detail="Limits must be positive")
        
        if daily_limit > weekly_limit or weekly_limit > monthly_limit:
            raise HTTPException(status_code=400, detail="Daily ≤ Weekly ≤ Monthly limits")
        
        # Update user's membership limits
        from app.models import ClassMembership
        target_membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.user_id == user_id
        ).first()
        
        if not target_membership:
            raise HTTPException(status_code=404, detail="User membership not found")
        
        target_membership.daily_token_limit = daily_limit
        target_membership.weekly_token_limit = weekly_limit
        target_membership.monthly_token_limit = monthly_limit
        
        db.commit()
        
        logger.info(f"Token limits updated for user {user_id} in class {class_id}")
        return {
            "message": "Limits updated successfully",
            "daily_limit": daily_limit,
            "weekly_limit": weekly_limit,
            "monthly_limit": monthly_limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user limits: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

