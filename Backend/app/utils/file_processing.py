import PyPDF2
import docx
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

class FileProcessor:
    
    def extract_text(self, file_path: str) -> str:
        """Extract text content from various file types"""
        try:
            file_ext = file_path.split('.')[-1].lower()
            
            if file_ext == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext == 'txt':
                return self._extract_from_txt(file_path)
            elif file_ext == 'docx':
                return self._extract_from_docx(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e2:
                logger.error(f"Error reading TXT {file_path}: {e2}")
                return ""
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # If this isn't the last chunk, try to end at a sentence boundary
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                sentence_endings = ['. ', '! ', '? ', '\n']
                best_end = end
                
                # Search backwards from the end position for a sentence ending
                for i in range(end, max(start + chunk_size // 2, start), -1):
                    if text[i:i+2] in sentence_endings:
                        best_end = i + 1
                        break
                
                end = best_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position (with overlap)
            start = max(start + 1, end - overlap)
            
            # Avoid infinite loop
            if start >= text_length:
                break
        
        return chunks

