from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Document, DocumentScope, Class, ClassMembership, ChatSession
from app.schemas.document_schemas import (
    DocumentUploadResponse,
    DocumentUpdateRequest,
    DocumentListResponse,
    YouTubeVideoRequest
)
from app.utils.security import get_current_user
from app.schemas import UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/classes/{class_id}/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_class_document(
    class_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Upload a document to a class.
    
    PLACEHOLDER: File processing will be implemented in Phase 3.
    Currently just creates database record.
    """
    try:
        # Check if class exists
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check if user is member
        membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this class")
        
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Create document record
        document = Document(
            filename=file.filename,
            original_filename=file.filename,
            file_path=f"uploads/{class_id}/{file.filename}",  # PLACEHOLDER
            file_type=file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown',
            file_size=file.size or 0,
            description=description,
            scope=DocumentScope.CLASS,
            class_id=class_id,
            uploaded_by=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Document {document.id} uploaded to class {class_id} by user {current_user.id}")
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            description=document.description,
            url=document.url,
            scope=document.scope.value,
            class_id=document.class_id,
            session_id=document.session_id,
            uploaded_at=document.uploaded_at,
            processing_status=document.processing_status.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.post("/classes/{class_id}/upload-youtube", response_model=DocumentUploadResponse, status_code=201)
async def upload_youtube_video(
    class_id: int,
    video: YouTubeVideoRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Add a YouTube video to a class.
    
    PLACEHOLDER: Video processing will be implemented in Phase 3.
    """
    try:
        # Check if class exists
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check if user is member
        membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this class")
        
        # Extract video ID
        video_url = str(video.url)
        video_id = _extract_youtube_id(video_url)
        
        # Create document record
        document = Document(
            filename=f"YouTube: {video_id}",
            original_filename=video_url,
            file_path="",
            file_type="youtube",
            file_size=0,
            description=video.description,
            url=video_url,
            scope=DocumentScope.CLASS,
            class_id=class_id,
            uploaded_by=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"YouTube video {video_id} added to class {class_id} by user {current_user.id}")
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            description=document.description,
            url=document.url,
            scope=document.scope.value,
            class_id=document.class_id,
            session_id=document.session_id,
            uploaded_at=document.uploaded_at,
            processing_status=document.processing_status.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding YouTube video: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add YouTube video")


@router.get("/classes/{class_id}", response_model=DocumentListResponse)
async def get_class_documents(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get all documents for a class.
    """
    try:
        # Check if user is member
        membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this class")
        
        documents = db.query(Document).filter(
            Document.class_id == class_id,
            Document.scope == DocumentScope.CLASS
        ).order_by(Document.uploaded_at.desc()).all()
        
        return DocumentListResponse(
            documents=[
                DocumentUploadResponse(
                    id=doc.id,
                    filename=doc.filename,
                    original_filename=doc.original_filename,
                    file_type=doc.file_type,
                    file_size=doc.file_size,
                    description=doc.description,
                    url=doc.url,
                    scope=doc.scope.value,
                    class_id=doc.class_id,
                    session_id=doc.session_id,
                    uploaded_at=doc.uploaded_at,
                    processing_status=doc.processing_status.value
                )
                for doc in documents
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@router.put("/{document_id}", response_model=DocumentUploadResponse)
async def update_document(
    document_id: int,
    update_data: DocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update document description.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if user has access
        membership = db.query(ClassMembership).filter(
            ClassMembership.class_id == document.class_id,
            ClassMembership.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Not authorized to update this document")
        
        # Update description
        if update_data.description is not None:
            document.description = update_data.description
        
        db.commit()
        db.refresh(document)
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            description=document.description,
            url=document.url,
            scope=document.scope.value,
            class_id=document.class_id,
            session_id=document.session_id,
            uploaded_at=document.uploaded_at,
            processing_status=document.processing_status.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update document")


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a document.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if user is owner of class or uploaded the document
        class_obj = db.query(Class).filter(Class.id == document.class_id).first()
        
        if class_obj.owner_id != current_user.id and document.uploaded_by != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this document")
        
        db.delete(document)
        db.commit()
        
        logger.info(f"Document {document_id} deleted by user {current_user.id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


def _extract_youtube_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'watch?v=' in url:
        return url.split('watch?v=')[1].split('&')[0]
    elif 'youtube.com/embed/' in url:
        return url.split('embed/')[1].split('?')[0]
    return url


