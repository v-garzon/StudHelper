from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    description: Optional[str]
    url: Optional[str]
    scope: str
    class_id: int
    session_id: Optional[int]
    uploaded_at: datetime
    processing_status: str
    
    class Config:
        from_attributes = True


class DocumentUpdateRequest(BaseModel):
    description: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentUploadResponse]


class YouTubeVideoRequest(BaseModel):
    url: HttpUrl
    description: Optional[str] = None


