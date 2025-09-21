"""PDF document processor."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

import pdfplumber
import pypdf
from io import BytesIO

from .base import DocumentProcessor

logger = logging.getLogger(__name__)


class PDFProcessor(DocumentProcessor):
    """PDF document processor."""
    
    def __init__(self):
        super().__init__()
        self.supported_types = ["pdf", "application/pdf"]
    
    async def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process PDF file and extract text content."""
        try:
            # Determine processing method
            if await self._is_simple_pdf(file_path):
                result = await self._process_with_pypdf(file_path)
            else:
                result = await self._process_with_pdfplumber(file_path)
            
            result.update({
                "file_type": "pdf",
                "processor": "PDFProcessor",
                "file_path": str(file_path),
            })
            
            return result
            
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "chunks": [],
                "metadata": {"file_type": "pdf", "error": str(e)},
            }
    
    async def _is_simple_pdf(self, file_path: Path) -> bool:
        """Check if PDF is simple enough for pypdf."""
        def check():
            try:
                with open(file_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    if len(reader.pages) > 0:
                        page_text = reader.pages[0].extract_text()
                        # Simple heuristic: if no tables or complex formatting
                        return '\t' not in page_text and '|' not in page_text
                return True
            except:
                return False
        
        return await self._run_in_thread(check)
    
    async def _process_with_pypdf(self, file_path: Path) -> Dict[str, Any]:
        """Process simple PDFs with pypdf."""
        def extract():
            chunks = []
            metadata = {
                "extraction_method": "pypdf",
                "pages": 0,
                "word_count": 0,
            }
            
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text().strip()
                    if text:
                        chunks.append({
                            "content": text,
                            "metadata": self._create_chunk_metadata(
                                source=str(file_path),
                                page=page_num + 1,
                                chunk_index=len(chunks),
                                extraction_method="pypdf",
                            ),
                        })
                        metadata["word_count"] += len(text.split())
                
                metadata["pages"] = len(reader.pages)
            
            return {
                "success": True,
                "chunks": chunks,
                "metadata": metadata,
            }
        
        return await self._run_in_thread(extract)
    
    async def _process_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """Process complex PDFs with pdfplumber."""
        def extract():
            chunks = []
            metadata = {
                "extraction_method": "pdfplumber",
                "pages": 0,
                "word_count": 0,
                "tables_found": 0,
            }
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text and text.strip():
                        chunks.append({
                            "content": text.strip(),
                            "metadata": self._create_chunk_metadata(
                                source=str(file_path),
                                page=page_num + 1,
                                chunk_index=len(chunks),
                                extraction_method="pdfplumber",
                            ),
                        })
                        metadata["word_count"] += len(text.split())
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if table:
                            table_text = self._table_to_text(table)
                            if table_text:
                                chunks.append({
                                    "content": table_text,
                                    "metadata": self._create_chunk_metadata(
                                        source=str(file_path),
                                        page=page_num + 1,
                                        chunk_index=len(chunks),
                                        table_index=table_idx,
                                        content_type="table",
                                        extraction_method="pdfplumber",
                                    ),
                                })
                                metadata["tables_found"] += 1
                
                metadata["pages"] = len(pdf.pages)
            
            return {
                "success": True,
                "chunks": chunks,
                "metadata": metadata,
            }
        
        return await self._run_in_thread(extract)
    
    def _table_to_text(self, table: List[List[str]]) -> str:
        """Convert table to readable text."""
        if not table or not table[0]:
            return ""
        
        text_parts = []
        for row in table:
            if row:
                clean_row = [cell.strip() if cell else "" for cell in row]
                text_parts.append(" | ".join(clean_row))
        
        return "\n".join(text_parts)

