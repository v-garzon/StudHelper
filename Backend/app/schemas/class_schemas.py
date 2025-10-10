from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class DocumentSummary(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    description: Optional[str]
    url: Optional[str]
    uploaded_at: datetime
    processing_status: str
    
    class Config:
        from_attributes = True


class ClassResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    class_code: str
    owner_id: int
    created_at: datetime
    is_owner: bool = False
    chat_session_count: int = 0
    document_count: int = 0
    member_count: int = 0
    
    class Config:
        from_attributes = True


class ClassDetailResponse(ClassResponse):
    documents: List[DocumentSummary] = []
    
    class Config:
        from_attributes = True


class ClassListResponse(BaseModel):
    classes: List[ClassResponse]


