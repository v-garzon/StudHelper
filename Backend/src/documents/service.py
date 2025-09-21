"""Document processing service."""

import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.documents.models import Document, DocumentChunk
from src.documents.processors.pdf_processor import PDFProcessor
from src.documents.processors.docx_processor import DocxProcessor
from src.documents.processors.youtube_processor import YouTubeProcessor
from src.documents.schemas import DocumentResponse, DocumentProcessingResult
from src.core.exceptions import NotFoundError, ProcessingError, ValidationError
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Document processing service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.processors = {
            "pdf": PDFProcessor(),
            "docx": DocxProcessor(),
            "youtube": YouTubeProcessor(),
        }
    
    async def upload_document(
        self,
        user_id: int,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None,
    ) -> Document:
        """Upload and store document."""
        # Validate file
        file_type = self._get_file_type(filename, content_type)
        if not self._is_supported_type(file_type):
            raise ValidationError(f"Unsupported file type: {file_type}")
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=self._sanitize_filename(filename),
            original_filename=filename,
            file_type=file_type,
            file_size=len(file_content),
            status="pending",
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        # Save file
        file_path = await self._save_file(document.id, file_content, filename)
        document.file_path = str(file_path)
        await self.db.commit()
        
        logger.info(f"Uploaded document: {filename} (ID: {document.id})")
        return document
    
    async def process_document(self, document_id: int) -> DocumentProcessingResult:
        """Process document and extract content."""
        document = await self._get_document(document_id)
        if not document:
            raise NotFoundError("Document not found")
        
        if document.status == "completed":
            return DocumentProcessingResult(
                success=True,
                document_id=document_id,
                message="Document already processed",
            )
        
        try:
            document.status = "processing"
            await self.db.commit()
            
            start_time = time.time()
            
            # Process based on file type
            if document.file_type == "youtube":
                # For YouTube, we need the URL (stored in metadata or filename)
                result = await self.processors["youtube"].process(document.original_filename)
            else:
                # For file-based documents
                file_path = Path(document.file_path)
                if not file_path.exists():
                    raise ProcessingError(f"File not found: {file_path}")
                
                processor = self._get_processor(document.file_type)
                result = await processor.process(file_path)
            
            processing_time = time.time() - start_time
            
            if result["success"]:
                # Store extracted content
                document.content = result["chunks"][0]["content"] if result["chunks"] else ""
                document.metadata = str(result["metadata"])
                document.page_count = result["metadata"].get("pages", len(result["chunks"]))
                document.word_count = result["metadata"].get("word_count", 0)
                document.processing_time = processing_time
                document.status = "completed"
                
                # Create chunks
                chunks_created = await self._create_chunks(document_id, result["chunks"])
                
                await self.db.commit()
                
                logger.info(f"Processed document {document_id}: {chunks_created} chunks created")
                
                return DocumentProcessingResult(
                    success=True,
                    document_id=document_id,
                    message=f"Document processed successfully",
                    chunks_created=chunks_created,
                    processing_time=processing_time,
                )
            else:
                document.status = "failed"
                document.metadata = str({"error": result.get("error", "Unknown error")})
                await self.db.commit()
                
                return DocumentProcessingResult(
                    success=False,
                    document_id=document_id,
                    message=f"Processing failed: {result.get('error', 'Unknown error')}",
                    errors=[result.get("error", "Unknown error")],
                )
        
        except Exception as e:
            document.status = "failed"
            document.metadata = str({"error": str(e)})
            await self.db.commit()
            
            logger.error(f"Document processing failed: {str(e)}")
            raise ProcessingError(f"Processing failed: {str(e)}")
    
    async def add_youtube_video(self, user_id: int, url: str, title: Optional[str] = None) -> Document:
        """Add YouTube video for processing."""
        # Validate YouTube URL
        if not self._is_valid_youtube_url(url):
            raise ValidationError("Invalid YouTube URL")
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=title or f"YouTube Video - {url.split('/')[-1]}",
            original_filename=url,  # Store URL as filename
            file_type="youtube",
            status="pending",
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        logger.info(f"Added YouTube video: {url} (ID: {document.id})")
        return document
    
    async def get_user_documents(self, user_id: int) -> List[DocumentResponse]:
        """Get all documents for a user."""
        result = await self.db.execute(
            select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        )
        documents = result.scalars().all()
        return [DocumentResponse.model_validate(doc) for doc in documents]
    
    async def get_document(self, document_id: int, user_id: int) -> Optional[DocumentResponse]:
        """Get specific document."""
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id
            )
        )
        document = result.scalar_one_or_none()
        return DocumentResponse.model_validate(document) if document else None
    
    async def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete document and its chunks."""
        document = await self._get_document(document_id, user_id)
        if not document:
            return False
        
        # Delete file if it exists
        if document.file_path:
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
        
        # Delete chunks
        await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        
        # Delete document
        await self.db.delete(document)
        await self.db.commit()
        
        logger.info(f"Deleted document {document_id}")
        return True
    
    # Private methods
    
    async def _get_document(self, document_id: int, user_id: Optional[int] = None) -> Optional[Document]:
        """Get document by ID."""
        query = select(Document).where(Document.id == document_id)
        if user_id is not None:
            query = query.where(Document.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _save_file(self, document_id: int, content: bytes, filename: str) -> Path:
        """Save uploaded file to disk."""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Create unique filename
        file_path = upload_dir / f"{document_id}_{self._sanitize_filename(filename)}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_path
    
    async def _create_chunks(self, document_id: int, chunks: List[Dict[str, Any]]) -> int:
        """Create document chunks in database."""
        chunk_objects = []
        
        for i, chunk in enumerate(chunks):
            chunk_obj = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=chunk["content"],
                metadata=str(chunk.get("metadata", {})),
                start_char=chunk.get("metadata", {}).get("start_char"),
                end_char=chunk.get("metadata", {}).get("end_char"),
                page_number=chunk.get("metadata", {}).get("page"),
            )
            chunk_objects.append(chunk_obj)
        
        self.db.add_all(chunk_objects)
        await self.db.commit()
        
        return len(chunk_objects)
    
    def _get_file_type(self, filename: str, content_type: Optional[str] = None) -> str:
        """Determine file type from filename and content type."""
        if content_type:
            return content_type
        
        # Guess from filename
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            return mime_type
        
        # Fall back to extension
        ext = Path(filename).suffix.lower()
        ext_mapping = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".txt": "text/plain",
        }
        
        return ext_mapping.get(ext, "application/octet-stream")
    
    def _is_supported_type(self, file_type: str) -> bool:
        """Check if file type is supported."""
        supported_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "text/plain",
            "youtube",
        ]
        return file_type in supported_types
    
    def _get_processor(self, file_type: str):
        """Get appropriate processor for file type."""
        processor_mapping = {
            "application/pdf": "pdf",
            "pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "docx": "docx",
            "youtube": "youtube",
        }
        
        processor_type = processor_mapping.get(file_type)
        if not processor_type or processor_type not in self.processors:
            raise ProcessingError(f"No processor available for file type: {file_type}")
        
        return self.processors[processor_type]
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage."""
        import re
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[^\w\-_\. ]', '', filename)
        return sanitized[:100]  # Limit length
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """Validate YouTube URL."""
        import re
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url.strip()):
                return True
        return False

