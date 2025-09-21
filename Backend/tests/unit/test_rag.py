"""RAG system tests."""

import pytest
from unittest.mock import AsyncMock

from src.rag.chunking import TextChunker, AdaptiveChunker
from src.rag.service import RAGService


class TestTextChunker:
    """Test text chunking."""
    
    def test_basic_chunking(self):
        """Test basic text chunking."""
        chunker = TextChunker(chunk_size=100, overlap=20)
        
        text = "This is a test. " * 20  # Long text
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 1
        assert all(len(chunk["content"]) <= 120 for chunk in chunks)  # Allow some flexibility
        assert all("chunk_index" in chunk["metadata"] for chunk in chunks)
    
    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        
        chunks = chunker.chunk_text("")
        assert chunks == []
        
        chunks = chunker.chunk_text("   ")
        assert chunks == []


class TestAdaptiveChunker:
    """Test adaptive chunking."""
    
    def test_content_type_detection(self):
        """Test content type detection."""
        chunker = AdaptiveChunker()
        
        # Code content
        code_text = "def function():\n    return True\nclass MyClass:\n    pass"
        code_type = chunker._determine_content_type(code_text, {})
        assert code_type == "code"
        
        # Academic content
        academic_text = "Abstract: This paper presents a methodology for testing..."
        academic_type = chunker._determine_content_type(academic_text, {})
        assert academic_type == "academic"

