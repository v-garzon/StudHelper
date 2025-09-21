"""Document schemas."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    """Document upload schema."""
    filename: str
    file_type: str
    file_size: Optional[int] = None


class DocumentResponse(BaseModel):
    """Document response schema."""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: Optional[int]
    status: str
    page_count: Optional[int]
    word_count: Optional[int]
    processing_time: Optional[float]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentProcessingResult(BaseModel):
    """Document processing result."""
    success: bool
    document_id: int
    message: str
    chunks_created: Optional[int] = None
    processing_time: Optional[float] = None
    errors: Optional[List[str]] = None


class YouTubeUpload(BaseModel):
    """YouTube upload schema."""
    url: str = Field(..., description="YouTube video URL")
    title: Optional[str] = None


class DocumentStats(BaseModel):
    """Document statistics."""
    total_documents: int
    total_pages: int
    total_words: int
    by_type: Dict[str, int]
    processing_status: Dict[str, int]

