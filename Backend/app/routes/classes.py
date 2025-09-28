from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import ClassCreate, ClassResponse, JoinClassRequest, UserResponse
from app.services.permission_service import PermissionService
from app.utils.security import get_current_user
import logging
import string
import secrets

router = APIRouter()
logger = logging.getLogger(__name__)

def generate_class_code() -> str:
    """Generate a unique 8-character class code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new class"""
    try:
        from app.models import Class, ClassMembership
        
        # Generate unique class code
        class_code = generate_class_code()
        while db.query(Class).filter(Class.class_code == class_code).first():
            class_code = generate_class_code()
        
        # Create class
        new_class = Class(
            name=class_data.name,
            description=class_data.description,
            class_code=class_code,
            owner_id=current_user.id
        )
        db.add(new_class)
        db.flush()
        
        # Add owner as manager
        owner_membership = ClassMembership(
            user_id=current_user.id,
            class_id=new_class.id,
            is_manager=True,
            can_read=True,
            can_chat=True,
            can_share_class=True,
            can_upload_documents=True,
            max_concurrent_chats=10  # Managers get more chats
        )
        db.add(owner_membership)
        db.commit()
        db.refresh(new_class)
        
        # Add member count
        result = ClassResponse.model_validate(new_class)
        result.member_count = 1
        
        logger.info(f"Class created: {new_class.name} by {current_user.username}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating class: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[ClassResponse])
async def get_user_classes(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get classes where user is owner or member"""
    try:
        from app.models import Class, ClassMembership
        
        # Get classes where user is a member
        memberships = db.query(ClassMembership).filter(
            ClassMembership.user_id == current_user.id
        ).all()
        
        classes = []
        for membership in memberships:
            class_obj = membership.class_obj
            if class_obj.is_active:
                # Count members
                member_count = db.query(ClassMembership).filter(
                    ClassMembership.class_id == class_obj.id
                ).count()
                
                result = ClassResponse.model_validate(class_obj)
                result.member_count = member_count
                classes.append(result)
        
        return classes
        
    except Exception as e:
        logger.error(f"Error getting user classes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/join", response_model=ClassResponse)
async def join_class(
    join_data: JoinClassRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a class using class code"""
    try:
        from app.models import Class, ClassMembership
        
        # Find class by code
        class_obj = db.query(Class).filter(
            Class.class_code == join_data.class_code,
            Class.is_active == True
        ).first()
        
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check if already a member
        existing_membership = db.query(ClassMembership).filter(
            ClassMembership.user_id == current_user.id,
            ClassMembership.class_id == class_obj.id
        ).first()
        
        if existing_membership:
            raise HTTPException(status_code=400, detail="Already a member of this class")
        
        # Create membership with default permissions
        membership = ClassMembership(
            user_id=current_user.id,
            class_id=class_obj.id,
            is_manager=False,
            can_read=True,
            can_chat=True,
            can_share_class=False,
            can_upload_documents=True,
            max_concurrent_chats=3
        )
        db.add(membership)
        db.commit()
        
        # Get member count
        member_count = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_obj.id
        ).count()
        
        result = ClassResponse.model_validate(class_obj)
        result.member_count = member_count
        
        logger.info(f"User {current_user.username} joined class {class_obj.name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining class: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{class_id}", response_model=ClassResponse)
async def get_class_details(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get class details"""
    try:
        permission_service = PermissionService()
        
        # Check if user has access to this class
        membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
        
        class_obj = membership.class_obj
        if not class_obj.is_active:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Get member count
        from app.models import ClassMembership
        member_count = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id
        ).count()
        
        result = ClassResponse.model_validate(class_obj)
        result.member_count = member_count
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{class_id}")
async def delete_class(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a class (owner only)"""
    try:
        from app.models import Class
        
        class_obj = db.query(Class).filter(
            Class.id == class_id,
            Class.owner_id == current_user.id
        ).first()
        
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found or access denied")
        
        # Soft delete
        class_obj.is_active = False
        db.commit()
        
        logger.info(f"Class deleted: {class_obj.name} by {current_user.username}")
        return {"message": "Class successfully deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting class: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

