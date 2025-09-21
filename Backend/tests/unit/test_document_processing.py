"""Document processing tests."""

import pytest
from pathlib import Path
import tempfile

from src.documents.service import DocumentService
from src.documents.processors.pdf_processor import PDFProcessor


class TestDocumentService:
    """Test document service."""
    
    async def test_upload_document(self, db_session, test_user, sample_pdf_content):
        """Test document upload."""
        service = DocumentService(db_session)
        
        document = await service.upload_document(
            user_id=test_user.id,
            file_content=sample_pdf_content,
            filename="test.pdf",
            content_type="application/pdf",
        )
        
        assert document.filename == "test.pdf"
        assert document.file_type == "application/pdf"
        assert document.file_size == len(sample_pdf_content)
        assert document.status == "pending"
    
    async def test_add_youtube_video(self, db_session, test_user):
        """Test adding YouTube video."""
        service = DocumentService(db_session)
        
        document = await service.add_youtube_video(
            user_id=test_user.id,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            title="Test Video",
        )
        
        assert document.filename == "Test Video"
        assert document.original_filename == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert document.file_type == "youtube"


class TestPDFProcessor:
    """Test PDF processor."""
    
    def test_can_process(self):
        """Test processor type checking."""
        processor = PDFProcessor()
        
        assert processor.can_process("pdf")
        assert processor.can_process("application/pdf")
        assert not processor.can_process("docx")

