"""Text chunking strategies."""

import logging
from typing import Dict, List, Any
import re

logger = logging.getLogger(__name__)


class TextChunker:
    """Text chunking utility."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        if not text or not text.strip():
            return []
        
        # Clean text
        text = self._clean_text(text)
        
        # Choose chunking strategy based on content
        if self._is_structured_content(text):
            chunks = self._chunk_by_structure(text)
        else:
            chunks = self._chunk_by_sentences(text)
        
        # Add metadata to chunks
        result = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk),
                "word_count": len(chunk.split()),
                **(metadata or {}),
            }
            
            result.append({
                "content": chunk,
                "metadata": chunk_metadata,
            })
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines but preserve paragraph breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _is_structured_content(self, text: str) -> bool:
        """Check if text has clear structure (headers, lists, etc.)."""
        structure_indicators = [
            r'^#{1,6}\s',  # Markdown headers
            r'^\d+\.\s',   # Numbered lists
            r'^[•\-\*]\s', # Bullet points
            r'^[A-Z][^.!?]*:'
,  # Section headers ending with colon
        ]
        
        lines = text.split('\n')
        structured_lines = 0
        
        for line in lines:
            line = line.strip()
            if line:
                for pattern in structure_indicators:
                    if re.match(pattern, line, re.MULTILINE):
                        structured_lines += 1
                        break
        
        # If more than 10% of lines show structure, use structural chunking
        return structured_lines / max(len([l for l in lines if l.strip()]), 1) > 0.1
    
    def _chunk_by_structure(self, text: str) -> List[str]:
        """Chunk text by preserving structure."""
        chunks = []
        current_chunk = ""
        
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                current_chunk = self._get_overlap_text(current_chunk) + paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk text by sentences with overlap."""
        # Split into sentences
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_sentences = []
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_sentences)
                current_chunk = " ".join(overlap_sentences + [sentence])
                current_sentences = overlap_sentences + [sentence]
            else:
                current_chunk = test_chunk
                current_sentences.append(sentence)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (could be improved with spaCy/NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of chunk."""
        if len(text) <= self.overlap:
            return text
        
        # Try to find a good break point
        overlap_text = text[-self.overlap:]
        
        # Find the start of a sentence in the overlap
        sentences = self._split_sentences(overlap_text)
        if len(sentences) > 1:
            return " ".join(sentences[1:])
        
        return overlap_text
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get overlap sentences for new chunk."""
        if not sentences:
            return []
        
        # Calculate how many sentences to include for overlap
        overlap_text = ""
        overlap_sentences = []
        
        for sentence in reversed(sentences):
            test_overlap = sentence + " " + overlap_text if overlap_text else sentence
            if len(test_overlap) <= self.overlap:
                overlap_text = test_overlap
                overlap_sentences.insert(0, sentence)
            else:
                break
        
        return overlap_sentences


class AdaptiveChunker(TextChunker):
    """Adaptive chunker that adjusts strategy based on content type."""
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Adaptively chunk text based on content characteristics."""
        if not text or not text.strip():
            return []
        
        # Determine content type
        content_type = self._determine_content_type(text, metadata or {})
        
        # Adjust chunking parameters based on content type
        if content_type == "code":
            self.chunk_size = 800  # Smaller chunks for code
            self.overlap = 100
        elif content_type == "academic":
            self.chunk_size = 1200  # Larger chunks for academic content
            self.overlap = 300
        elif content_type == "transcript":
            self.chunk_size = 1500  # Large chunks for transcripts
            self.overlap = 150
        else:
            self.chunk_size = 1000  # Default
            self.overlap = 200
        
        return super().chunk_text(text, metadata)
    
    def _determine_content_type(self, text: str, metadata: Dict[str, Any]) -> str:
        """Determine content type from text and metadata."""
        # Check metadata first
        if metadata.get("content_type") == "table":
            return "table"
        if metadata.get("file_type") == "youtube":
            return "transcript"
        
        # Analyze text content
        code_indicators = len(re.findall(r'[{}\[\]();]|def |class |import |from ', text))
        academic_indicators = len(re.findall(r'\b(abstract|introduction|methodology|conclusion|references)\b', text, re.IGNORECASE))
        
        if code_indicators > 10:
            return "code"
        elif academic_indicators > 2:
            return "academic"
        elif "transcript" in text.lower() or metadata.get("extraction_method") == "whisper":
            return "transcript"
        else:
            return "general"

