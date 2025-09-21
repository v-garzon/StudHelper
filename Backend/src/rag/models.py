"""RAG-related models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class VectorEmbedding(Base):
    """Vector embedding model."""
    
    __tablename__ = "vector_embeddings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"))
    chunk_id: Mapped[int] = mapped_column(Integer, ForeignKey("document_chunks.id"))
    
    # Vector information
    vector_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # ChromaDB ID
    embedding_model: Mapped[str] = mapped_column(String(100))
    
    # Metadata
    content_preview: Mapped[str] = mapped_column(Text)  # First 200 chars for reference
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

