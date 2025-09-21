"""RAG API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.database import get_db_session
from src.core.deps import get_default_user
from src.rag.schemas import SearchQuery, SearchResponse
from src.rag.service import RAGService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    search_query: SearchQuery,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Search documents using semantic similarity."""
    rag_service = RAGService(db)
    
    # Use current user if not specified in query
    if search_query.user_id is None:
        search_query.user_id = user.id
    
    return await rag_service.search_knowledge_base(
        query=search_query.query,
        user_id=search_query.user_id,
        document_ids=search_query.document_ids,
        limit=search_query.limit,
    )


@router.get("/context/{query}")
async def get_context_for_query(
    query: str,
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get context for a specific query."""
    rag_service = RAGService(db)
    
    context_data = await rag_service.get_context_for_chat(
        query=query,
        user_id=user.id,
    )
    
    return context_data


@router.get("/stats")
async def get_rag_stats(
    user: User = Depends(get_default_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get RAG system statistics."""
    rag_service = RAGService(db)
    
    # Get vector store stats
    stats = await rag_service.vector_store.get_collection_stats()
    
    return stats


