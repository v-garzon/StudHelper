from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.database import get_db
from app.services.class_service import ClassService
from app.schemas.class_schemas import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassDetailResponse,
    ClassListResponse
)
from app.utils.security import get_current_user
from app.schemas import UserResponse
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ClassDetailResponse, status_code=201)
async def create_class(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    file_descriptions: Optional[str] = Form(None),  # JSON string
    youtube_urls: Optional[str] = Form(None),  # JSON string
    youtube_descriptions: Optional[str] = Form(None),  # JSON string
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new class with optional documents.
    
    - **name**: Class name (required)
    - **description**: Class description (optional)
    - **files**: Upload files (optional, multiple)
    - **file_descriptions**: JSON object mapping filenames to descriptions
    - **youtube_urls**: JSON array of YouTube URLs
    - **youtube_descriptions**: JSON array of descriptions for YouTube videos
    """
    try:
        # Parse JSON strings
        file_desc_dict = json.loads(file_descriptions) if file_descriptions else {}
        youtube_url_list = json.loads(youtube_urls) if youtube_urls else []
        youtube_desc_list = json.loads(youtube_descriptions) if youtube_descriptions else []
        
        new_class = await ClassService.create_class(
            db=db,
            name=name,
            description=description,
            owner_id=current_user.id,
            files=files,
            file_descriptions=file_desc_dict,
            youtube_urls=youtube_url_list,
            youtube_descriptions=youtube_desc_list
        )
        
        return new_class
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in form data: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format in form data")
    except Exception as e:
        logger.error(f"Error creating class: {str(e)}")
        raise


@router.get("", response_model=ClassListResponse)
async def get_classes(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all classes the current user is a member of.
    
    Returns list of classes with basic info and counts.
    """
    classes = ClassService.get_user_classes(db, current_user.id)
    return ClassListResponse(classes=classes)


@router.get("/{class_id}", response_model=ClassDetailResponse)
async def get_class_details(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get detailed information about a specific class.
    
    Includes documents, member count, and session count.
    """
    return ClassService.get_class_details(db, class_id, current_user.id)


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_update: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update class information (owner only).
    
    Can update name and/or description.
    """
    return ClassService.update_class(
        db=db,
        class_id=class_id,
        user_id=current_user.id,
        name=class_update.name,
        description=class_update.description
    )


@router.delete("/{class_id}", status_code=204)
async def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a class and all related data (owner only).
    
    This will delete:
    - The class itself
    - All documents
    - All memberships
    - All chat sessions and messages
    """
    ClassService.delete_class(db, class_id, current_user.id)
    return None


