"""ChromaDB vector store integration."""

import asyncio
import logging
from typing import Dict, List, Any, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from src.config import get_settings
from src.rag.embeddings import EmbeddingService

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStore:
    """ChromaDB vector store wrapper."""
    
    def __init__(self):
        self.client = self._create_client()
        self.embedding_service = EmbeddingService()
        self.collection_name = "studhelper_documents"
        self.collection = None
        self._initialize_collection()
    
    def _create_client(self):
        """Create ChromaDB client."""
        try:
            # Try HTTP client first (production)
            client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            client.heartbeat()  # Test connection
            logger.info("Connected to ChromaDB server")
            return client
        except Exception:
            # Fall back to persistent client (development)
            logger.info("Using persistent ChromaDB client")
            return chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False,
                ),
            )
    
    def _initialize_collection(self):
        """Initialize or get collection."""
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
            )
            logger.info(f"Connected to existing collection: {self.collection_name}")
        except Exception:
            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "StudHelper document embeddings"},
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        user_id: Optional[int] = None,
    ) -> List[str]:
        """Add documents to vector store."""
        if not documents:
            return []
        
        try:
            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for i, doc in enumerate(documents):
                doc_id = f"doc_{user_id}_{i}_{hash(doc['content'])}"
                ids.append(doc_id)
                texts.append(doc["content"])
                
                metadata = doc.get("metadata", {})
                if user_id:
                    metadata["user_id"] = user_id
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings_result = await self.embedding_service.generate_embeddings(texts)
            embeddings = embeddings_result["embeddings"]
            
            # Add to ChromaDB
            await asyncio.to_thread(
                self.collection.add,
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        user_id: Optional[int] = None,
        document_ids: Optional[List[int]] = None,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_single_embedding(query)
            
            # Build where clause for filtering
            where = {}
            if user_id:
                where["user_id"] = user_id
            if document_ids:
                where["document_id"] = {"$in": document_ids}
            
            # Search
            results = await asyncio.to_thread(
                self.collection.query,
                query_embeddings=[query_embedding],
                n_results=k,
                where=where if where else None,
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                # Convert distance to similarity score (0-1)
                similarity = 1 - distance
                
                if similarity >= similarity_threshold:
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": similarity,
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            raise
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            await asyncio.to_thread(
                self.collection.delete,
                ids=ids,
            )
            logger.info(f"Deleted {len(ids)} documents from vector store")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    async def delete_user_documents(self, user_id: int) -> bool:
        """Delete all documents for a user."""
        try:
            await asyncio.to_thread(
                self.collection.delete,
                where={"user_id": user_id},
            )
            logger.info(f"Deleted all documents for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user documents: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = await asyncio.to_thread(self.collection.count)
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_service.model,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}

