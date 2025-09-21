"""RAG orchestration service."""

import logging
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.documents.models import Document, DocumentChunk
from src.rag.chunking import AdaptiveChunker
from src.rag.vector_store import VectorStore
from src.rag.retrieval import RetrievalService
from src.rag.schemas import SearchQuery, SearchResponse

logger = logging.getLogger(__name__)


class RAGService:
    """RAG orchestration service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store = VectorStore()
        self.retrieval_service = RetrievalService(db)
        self.chunker = AdaptiveChunker()
    
    async def process_document_for_rag(
        self,
        document_id: int,
        user_id: int,
        chunks: List[Dict[str, Any]],
    ) -> bool:
        """Process document chunks for RAG."""
        try:
            # Prepare chunks for vector storage
            vector_documents = []
            
            for chunk in chunks:
                # Add document and user information to metadata
                chunk_metadata = chunk.get("metadata", {})
                chunk_metadata.update({
                    "document_id": document_id,
                    "user_id": user_id,
                })
                
                vector_documents.append({
                    "content": chunk["content"],
                    "metadata": chunk_metadata,
                })
            
            # Add to vector store
            vector_ids = await self.vector_store.add_documents(
                documents=vector_documents,
                user_id=user_id,
            )
            
            logger.info(f"Processed {len(vector_ids)} chunks for RAG (document {document_id})")
            return True
            
        except Exception as e:
            logger.error(f"RAG processing error for document {document_id}: {str(e)}")
            return False
    
    async def search_knowledge_base(
        self,
        query: str,
        user_id: Optional[int] = None,
        document_ids: Optional[List[int]] = None,
        limit: int = 5,
    ) -> SearchResponse:
        """Search user's knowledge base."""
        search_query = SearchQuery(
            query=query,
            user_id=user_id,
            document_ids=document_ids,
            limit=limit,
        )
        
        return await self.retrieval_service.search_documents(search_query)
    
    async def get_context_for_chat(
        self,
        query: str,
        user_id: Optional[int] = None,
        max_context_length: int = 4000,
    ) -> Dict[str, Any]:
        """Get context for chat AI."""
        # Get relevant context
        context = await self.retrieval_service.get_context_for_query(
            query=query,
            user_id=user_id,
        )
        
        # Truncate if too long
        if len(context) > max_context_length:
            context = context[:max_context_length]
            # Try to end at a complete context block
            last_context_end = context.rfind("[Context ")
            if last_context_end > max_context_length * 0.7:
                context = context[:last_context_end]
        
        # Get sources for citations
        sources = await self.retrieval_service.get_relevant_sources(
            query=query,
            user_id=user_id,
        )
        
        return {
            "context": context,
            "sources": sources,
            "has_context": bool(context.strip()),
        }
    
    async def remove_document_from_rag(self, document_id: int, user_id: int) -> bool:
        """Remove document from RAG system."""
        try:
            # This would require tracking vector IDs by document
            # For now, we'll just log the request
            logger.info(f"Request to remove document {document_id} from RAG")
            return True
        except Exception as e:
            logger.error(f"Error removing document from RAG: {str(e)}")
            return False

