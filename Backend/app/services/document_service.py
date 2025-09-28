from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models import Document, DocumentChunk, DocumentScope, ProcessingStatus
from app.schemas import DocumentResponse
from app.utils.file_processing import FileProcessor
from app.utils.vector_operations import VectorOperations
from app.config import get_settings
import os
import uuid
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.file_processor = FileProcessor()
        self.vector_ops = VectorOperations()
    
    async def upload_class_document(self, db: Session, file: UploadFile, class_id: int, user_id: int) -> DocumentResponse:
        """Upload and process a class-level document"""
        return await self._upload_document(db, file, class_id, user_id, DocumentScope.CLASS)
    
    async def upload_session_document(self, db: Session, file: UploadFile, session_id: int, class_id: int, user_id: int) -> DocumentResponse:
        """Upload and process a session-specific document"""
        return await self._upload_document(db, file, class_id, user_id, DocumentScope.CHAT, session_id)
    
    async def _upload_document(self, db: Session, file: UploadFile, class_id: int, user_id: int, scope: DocumentScope, session_id: int = None) -> DocumentResponse:
        """Internal method to upload and process documents"""
        try:
            # Validate file
            await self._validate_file(file)
            
            # Generate unique filename
            file_ext = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Ensure upload directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Create document record
            document = Document(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_type=file_ext,
                file_size=len(content),
                scope=scope,
                class_id=class_id,
                session_id=session_id,
                uploaded_by=user_id,
                processing_status=ProcessingStatus.PENDING
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Process document asynchronously (in real implementation, use background task)
            await self._process_document(db, document)
            
            return DocumentResponse.model_validate(document)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            # Clean up file if it was created
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail="Error uploading document")
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_ext}' not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Reset file position for later reading
        await file.seek(0)
    
    async def _process_document(self, db: Session, document: Document):
        """Process document: extract text, chunk, and vectorize"""
        try:
            # Update status to processing
            document.processing_status = ProcessingStatus.PROCESSING
            db.commit()
            
            # Extract text from document
            text_content = self.file_processor.extract_text(document.file_path)
            
            if not text_content.strip():
                document.processing_status = ProcessingStatus.FAILED
                document.processing_error = "No text content found in document"
                db.commit()
                return
            
            # Chunk the text
            chunks = self.file_processor.chunk_text(text_content)
            
            # Create document chunks
            for i, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=document.id,
                    content=chunk_text,
                    chunk_index=i,
                    char_start=i * 1000,  # Approximate
                    char_end=min((i + 1) * 1000, len(text_content))
                )
                db.add(chunk)
            
            # Update status to completed
            document.processing_status = ProcessingStatus.COMPLETED
            db.commit()
            
            logger.info(f"Document processed successfully: {document.original_filename}")
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {e}")
            document.processing_status = ProcessingStatus.FAILED
            document.processing_error = str(e)
            db.commit()
    
    async def delete_document(self, db: Session, document_id: int):
        """Delete document and its chunks"""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError("Document not found")
            
            # Delete file from filesystem
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete chunks first (foreign key constraint)
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            
            # Delete document record
            db.delete(document)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            db.rollback()
            raise

