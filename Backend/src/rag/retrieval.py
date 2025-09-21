"""Document retrieval service."""

import logging
from typing import Dict, List, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.documents.models import Document, DocumentChunk
from src.rag.vector_store import VectorStore
from src.rag.schemas import SearchQuery, SearchResult, SearchResponse
import time

logger = logging.getLogger(__name__)


class RetrievalService:
    """Document retrieval service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store = VectorStore()
    
    async def search_documents(self, search_query: SearchQuery) -> SearchResponse:
        """Search documents using vector similarity."""
        start_time = time.time()
        
        try:
            # Perform vector search
            vector_results = await self.vector_store.similarity_search(
                query=search_query.query,
                k=search_query.limit,
                user_id=search_query.user_id,
                document_ids=search_query.document_ids,
                similarity_threshold=search_query.similarity_threshold,
            )
            
            # Enrich results with database information
            enriched_results = await self._enrich_results(vector_results)
            
            processing_time = time.time() - start_time
            
            return SearchResponse(
                query=search_query.query,
                results=enriched_results,
                total_results=len(enriched_results),
                processing_time=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise
    
    async def _enrich_results(self, vector_results: List[Dict[str, Any]]) -> List[SearchResult]:
        """Enrich vector search results with database information."""
        enriched_results = []
        
        for result in vector_results:
            metadata = result["metadata"]
            
            # Try to get document information
            document_id = metadata.get("document_id")
            chunk_id = metadata.get("chunk_id")
            
            if document_id:
                # Get document details
                doc_result = await self.db.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = doc_result.scalar_one_or_none()
                
                if document:
                    metadata.update({
                        "document_filename": document.filename,
                        "document_type": document.file_type,
                        "document_created": document.created_at.isoformat(),
                    })
            
            enriched_results.append(SearchResult(
                content=result["content"],
                score=result["score"],
                metadata=metadata,
                document_id=document_id,
                chunk_id=chunk_id,
            ))
        
        return enriched_results
    
    async def get_context_for_query(
        self,
        query: str,
        user_id: Optional[int] = None,
        max_contexts: int = 5,
    ) -> str:
        """Get relevant context for a query."""
        search_query = SearchQuery(
            query=query,
            user_id=user_id,
            limit=max_contexts,
            similarity_threshold=0.6,  # Lower threshold for context
        )
        
        search_response = await self.search_documents(search_query)
        
        if not search_response.results:
            return ""
        
        # Combine results into context
        context_parts = []
        for i, result in enumerate(search_response.results):
            context_parts.append(f"[Context {i+1}]: {result.content}")
        
        return "\n\n".join(context_parts)
    
    async def get_relevant_sources(
        self,
        query: str,
        user_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get relevant source documents for citations."""
        search_query = SearchQuery(
            query=query,
            user_id=user_id,
            limit=3,
            similarity_threshold=0.7,
        )
        
        search_response = await self.search_documents(search_query)
        
        sources = []
        seen_documents = set()
        
        for result in search_response.results:
            doc_id = result.document_id
            if doc_id and doc_id not in seen_documents:
                seen_documents.add(doc_id)
                sources.append({
                    "document_id": doc_id,
                    "filename": result.metadata.get("document_filename", "Unknown"),
                    "type": result.metadata.get("document_type", "unknown"),
                    "relevance_score": result.score,
                    "page": result.metadata.get("page"),
                })
        
        return sources

