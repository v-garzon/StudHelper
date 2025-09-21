"""Usage tracking routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db_session
from src.core.deps import get_default_user
from src.usage.schemas import UsageAnalytics, QuotaUpdate
from src.usage.service import UsageService

router = APIRouter()


@router.get("/analytics", response_model=UsageAnalytics)
async def get_usage_analytics(
    days: int = 30,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get usage analytics for the user."""
    usage_service = UsageService(db)
    return await usage_service.get_user_analytics(user.id, days)


@router.get("/limits")
async def get_current_limits(
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current usage limits and status."""
    usage_service = UsageService(db)
    return await usage_service.get_current_limits(user.id)


@router.put("/quotas")
async def update_quotas(
    quota_update: QuotaUpdate,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update user quotas."""
    usage_service = UsageService(db)
    success = await usage_service.update_quotas(user.id, quota_update)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quotas",
        )
    
    return {"message": "Quotas updated successfully"}


