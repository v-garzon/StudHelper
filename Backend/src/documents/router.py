"""Document processing routes."""

import asyncio
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db_session
from src.core.deps import get_current_user, get_default_user
from src.core.exceptions import NotFoundError, ProcessingError, ValidationError
from src.documents.schemas import (
    DocumentResponse,
    DocumentProcessingResult,
    YouTubeUpload,
    DocumentStats,
)
from src.documents.service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_default_user),  # Use default user for now
    db: AsyncSession = Depends(get_db_session),
):
    """Upload a document."""
    try:
        # Read file content
        content = await file.read()
        
        # Upload document
        document_service = DocumentService(db)
        document = await document_service.upload_document(
            user_id=user.id,
            file_content=content,
            filename=file.filename,
            content_type=file.content_type,
        )
        
        # Start processing in background
        asyncio.create_task(process_document_background(document.id, db))
        
        return DocumentResponse.model_validate(document)
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.post("/youtube", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_youtube_video(
    video_data: YouTubeUpload,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Add YouTube video for processing."""
    try:
        document_service = DocumentService(db)
        document = await document_service.add_youtube_video(
            user_id=user.id,
            url=video_data.url,
            title=video_data.title,
        )
        
        # Start processing in background
        asyncio.create_task(process_document_background(document.id, db))
        
        return DocumentResponse.model_validate(document)
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.post("/process/{document_id}", response_model=DocumentProcessingResult)
async def process_document(
    document_id: int,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Process a document."""
    try:
        document_service = DocumentService(db)
        result = await document_service.process_document(document_id)
        return result
        
    except (NotFoundError, ProcessingError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all user documents."""
    document_service = DocumentService(db)
    return await document_service.get_user_documents(user.id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get specific document."""
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id, user.id)
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete document."""
    document_service = DocumentService(db)
    success = await document_service.delete_document(document_id, user.id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


async def process_document_background(document_id: int, db: AsyncSession):
    """Background task to process document."""
    try:
        document_service = DocumentService(db)
        await document_service.process_document(document_id)
    except Exception as e:
        # Log error but don't raise (this is a background task)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Background processing failed for document {document_id}: {str(e)}")


