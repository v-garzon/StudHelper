from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import DocumentResponse, UserResponse
from app.services.permission_service import PermissionService
from app.services.document_service import DocumentService
from app.utils.security import get_current_user
from app.config import get_settings
import logging

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/classes/{class_id}/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_class_document(
    class_id: int,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document to a class (available to all class chats)"""
    try:
        permission_service = PermissionService()
        
        # Check if user can upload documents to this class
        membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not membership.can_upload_documents:
            raise HTTPException(status_code=403, detail="Document upload permission denied")
        
        # Upload and process document
        document_service = DocumentService()
        document = await document_service.upload_class_document(
            db, file, class_id, current_user.id
        )
        
        logger.info(f"Class document uploaded: {document.original_filename} by {current_user.username}")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading class document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sessions/{session_id}/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_session_document(
    session_id: int,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document to a specific chat session"""
    try:
        from app.models import ChatSession
        
        # Verify session ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Check upload permissions
        permission_service = PermissionService()
        membership = await permission_service.get_user_membership(db, current_user.id, session.class_id)
        if not membership.can_upload_documents:
            raise HTTPException(status_code=403, detail="Document upload permission denied")
        
        # Upload and process document
        document_service = DocumentService()
        document = await document_service.upload_session_document(
            db, file, session_id, session.class_id, current_user.id
        )
        
        logger.info(f"Session document uploaded: {document.original_filename} by {current_user.username}")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading session document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/classes/{class_id}", response_model=List[DocumentResponse])
async def get_class_documents(
    class_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents uploaded to a class"""
    try:
        permission_service = PermissionService()
        
        # Check if user has read access to this class
        membership = await permission_service.get_user_membership(db, current_user.id, class_id)
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not membership.can_read:
            raise HTTPException(status_code=403, detail="Read permission denied")
        
        from app.models import Document, DocumentScope
        
        # Get class documents
        documents = db.query(Document).filter(
            Document.class_id == class_id,
            Document.scope == DocumentScope.CLASS
        ).order_by(Document.uploaded_at.desc()).all()
        
        return [DocumentResponse.model_validate(doc) for doc in documents]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions/{session_id}", response_model=List[DocumentResponse])
async def get_session_documents(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents uploaded to a specific chat session"""
    try:
        from app.models import ChatSession, Document, DocumentScope
        
        # Verify session ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get session documents
        documents = db.query(Document).filter(
            Document.session_id == session_id,
            Document.scope == DocumentScope.CHAT
        ).order_by(Document.uploaded_at.desc()).all()
        
        return [DocumentResponse.model_validate(doc) for doc in documents]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document (uploader or class manager only)"""
    try:
        from app.models import Document
        
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if user can delete this document
        can_delete = False
        
        # Uploader can always delete their own documents
        if document.uploaded_by == current_user.id:
            can_delete = True
        else:
            # Class managers can delete class documents
            permission_service = PermissionService()
            membership = await permission_service.get_user_membership(db, current_user.id, document.class_id)
            if membership and membership.is_manager:
                can_delete = True
        
        if not can_delete:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Delete document and its chunks
        document_service = DocumentService()
        await document_service.delete_document(db, document_id)
        
        logger.info(f"Document deleted: {document.original_filename} by {current_user.username}")
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

