from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import MembershipResponse, PermissionUpdate, SponsorshipUpdate, UserResponse
from app.services.permission_service import PermissionService
from app.utils.security import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{class_id}/members", response_model=List[MembershipResponse])
async def get_class_members(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of a class (managers only)"""
    try:
        permission_service = PermissionService()
        
        # Check if user is manager of this class
        user_membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not user_membership or not user_membership.is_manager:
            raise HTTPException(status_code=403, detail="Only class managers can view members")
        
        from app.models import ClassMembership, User
        
        # Get all memberships with user details
        memberships = db.query(ClassMembership).join(User).filter(
            ClassMembership.class_id == class_id
        ).all()
        
        result = []
        for membership in memberships:
            member_data = MembershipResponse(
                id=membership.id,
                user_id=membership.user_id,
                username=membership.user.username,
                full_name=membership.user.full_name,
                joined_at=membership.joined_at,
                is_manager=membership.is_manager,
                can_read=membership.can_read,
                can_chat=membership.can_chat,
                max_concurrent_chats=membership.max_concurrent_chats,
                can_share_class=membership.can_share_class,
                can_upload_documents=membership.can_upload_documents,
                is_sponsored=membership.is_sponsored,
                daily_token_limit=membership.daily_token_limit,
                weekly_token_limit=membership.weekly_token_limit,
                monthly_token_limit=membership.monthly_token_limit
            )
            result.append(member_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class members: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{class_id}/members/{user_id}", response_model=MembershipResponse)
async def update_member_permissions(
    class_id: int,
    user_id: int,
    permission_update: PermissionUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member permissions (managers only)"""
    try:
        permission_service = PermissionService()
        
        # Check if current user is manager of this class
        user_membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not user_membership or not user_membership.is_manager:
            raise HTTPException(status_code=403, detail="Only class managers can update permissions")
        
        # Get target membership
        from app.models import ClassMembership
        target_membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.user_id == user_id
        ).first()
        
        if not target_membership:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Prevent manager from modifying their own manager status
        if user_id == current_user.id and hasattr(permission_update, 'is_manager'):
            raise HTTPException(status_code=400, detail="Cannot modify your own manager status")
        
        # Update permissions
        update_data = permission_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(target_membership, field):
                setattr(target_membership, field, value)
        
        db.commit()
        db.refresh(target_membership)
        
        # Return updated membership
        result = MembershipResponse(
            id=target_membership.id,
            user_id=target_membership.user_id,
            username=target_membership.user.username,
            full_name=target_membership.user.full_name,
            joined_at=target_membership.joined_at,
            is_manager=target_membership.is_manager,
            can_read=target_membership.can_read,
            can_chat=target_membership.can_chat,
            max_concurrent_chats=target_membership.max_concurrent_chats,
            can_share_class=target_membership.can_share_class,
            can_upload_documents=target_membership.can_upload_documents,
            is_sponsored=target_membership.is_sponsored,
            daily_token_limit=target_membership.daily_token_limit,
            weekly_token_limit=target_membership.weekly_token_limit,
            monthly_token_limit=target_membership.monthly_token_limit
        )
        
        logger.info(f"Member permissions updated for user {user_id} in class {class_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating member permissions: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{class_id}/sponsorship")
async def update_class_sponsorship(
    class_id: int,
    sponsorship_update: SponsorshipUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update class sponsorship settings (managers only)"""
    try:
        permission_service = PermissionService()
        
        # Check if current user is manager of this class
        user_membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not user_membership or not user_membership.is_manager:
            raise HTTPException(status_code=403, detail="Only class managers can update sponsorship")
        
        from app.models import ClassMembership
        
        # Update all non-manager memberships
        db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.is_manager == False
        ).update({
            "is_sponsored": sponsorship_update.is_sponsored
        })
        
        db.commit()
        
        action = "enabled" if sponsorship_update.is_sponsored else "disabled"
        logger.info(f"Class sponsorship {action} for class {class_id}")
        return {"message": f"Class sponsorship {action} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating class sponsorship: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

