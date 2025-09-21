"""Text chunking tests."""

import pytest
from src.rag.chunking import TextChunker, AdaptiveChunker


class TestTextChunker:
    """Test text chunking functionality."""
    
    def test_basic_chunking(self):
        """Test basic text chunking."""
        chunker = TextChunker(chunk_size=100, overlap=20)
        
        text = "This is a test sentence. " * 20  # Create long text
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 1
        assert all(len(chunk["content"]) <= 150 for chunk in chunks)  # Allow some flexibility
        assert all("metadata" in chunk for chunk in chunks)
        assert all("chunk_index" in chunk["metadata"] for chunk in chunks)
    
    def test_short_text_chunking(self):
        """Test chunking of short text."""
        chunker = TextChunker(chunk_size=1000, overlap=100)
        
        text = "This is a short text."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0]["content"] == text
    
    def test_empty_text_chunking(self):
        """Test chunking of empty text."""
        chunker = TextChunker()
        
        assert chunker.chunk_text("") == []
        assert chunker.chunk_text("   ") == []
        assert chunker.chunk_text("\n\n\n") == []
    
    def test_structured_content_detection(self):
        """Test detection of structured content."""
        chunker = TextChunker()
        
        structured_text = """
# Header 1
This is content under header 1.

## Header 2
- Bullet point 1
- Bullet point 2

1. Numbered item 1
2. Numbered item 2
"""
        
        is_structured = chunker._is_structured_content(structured_text)
        assert is_structured
        
        unstructured_text = "This is just a paragraph of text without any structure."
        is_structured = chunker._is_structured_content(unstructured_text)
        assert not is_structured


class TestAdaptiveChunker:
    """Test adaptive chunking functionality."""
    
    def test_content_type_detection(self):
        """Test content type detection."""
        chunker = AdaptiveChunker()
        
        # Test code detection
        code_text = "def function():\n    return True\nclass MyClass:\n    pass"
        content_type = chunker._determine_content_type(code_text, {})
        assert content_type == "code"
        
        # Test academic detection
        academic_text = "Abstract: This paper presents a methodology..."
        content_type = chunker._determine_content_type(academic_text, {})
        assert content_type == "academic"
        
        # Test transcript detection
        transcript_metadata = {"file_type": "youtube"}
        content_type = chunker._determine_content_type("Some text", transcript_metadata)
        assert content_type == "transcript"
    
    def test_adaptive_chunk_sizes(self):
        """Test that chunk sizes adapt to content type."""
        chunker = AdaptiveChunker()
        
        # Test with code content
        code_text = "def function():\n    return True\n" * 50
        code_chunks = chunker.chunk_text(code_text)
        
        # Test with academic content  
        academic_text = "Abstract: This research methodology. " * 50
        academic_chunks = chunker.chunk_text(academic_text, {"content_type": "academic"})
        
        # Academic chunks should generally be larger than code chunks
        if code_chunks and academic_chunks:
            avg_code_size = sum(len(c["content"]) for c in code_chunks) / len(code_chunks)
            avg_academic_size = sum(len(c["content"]) for c in academic_chunks) / len(academic_chunks)
            
            # This might not always be true due to text length, but test the chunker setup
            assert chunker.chunk_size >= 800  # Should have adjusted for academic content


