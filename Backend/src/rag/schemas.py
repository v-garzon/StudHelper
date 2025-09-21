"""RAG schemas."""

from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Search query schema."""
    query: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[int] = None
    document_ids: Optional[List[int]] = None
    limit: int = Field(5, ge=1, le=20)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Search result schema."""
    content: str
    score: float
    metadata: Dict[str, Any]
    document_id: Optional[int] = None
    chunk_id: Optional[int] = None


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: float


class EmbeddingRequest(BaseModel):
    """Embedding request schema."""
    texts: List[str]
    model: str = "text-embedding-3-large"


class EmbeddingResponse(BaseModel):
    """Embedding response schema."""
    embeddings: List[List[float]]
    model: str
    total_tokens: int

