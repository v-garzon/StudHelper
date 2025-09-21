"""Base document processor."""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentProcessor(ABC):
    """Abstract base class for document processors."""
    
    def __init__(self):
        self.supported_types: List[str] = []
    
    @abstractmethod
    async def process(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process document and return extracted content."""
        pass
    
    def can_process(self, file_type: str) -> bool:
        """Check if this processor can handle the file type."""
        return file_type.lower() in self.supported_types
    
    def _create_chunk_metadata(
        self,
        source: str,
        page: Optional[int] = None,
        chunk_index: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Create metadata for a content chunk."""
        metadata = {
            "source": source,
            "chunk_index": chunk_index,
            "processed_at": datetime.now().isoformat(),
            "processor": self.__class__.__name__,
        }
        
        if page is not None:
            metadata["page"] = page
        
        metadata.update(kwargs)
        return metadata
    
    async def _run_in_thread(self, func, *args, **kwargs):
        """Run CPU-bound operation in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

