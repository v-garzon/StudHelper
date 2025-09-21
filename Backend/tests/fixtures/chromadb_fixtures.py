"""ChromaDB mocking utilities for tests."""

from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock
import numpy as np


class MockChromaCollection:
    """Mock ChromaDB collection."""
    
    def __init__(self, name: str = "test_collection"):
        self.name = name
        self.documents = {}  # id -> document data
        self._id_counter = 0
    
    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict], embeddings: List[List[float]]):
        """Mock add operation."""
        for i, doc_id in enumerate(ids):
            self.documents[doc_id] = {
                "id": doc_id,
                "document": documents[i],
                "metadata": metadatas[i],
                "embedding": embeddings[i]
            }
    
    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        where: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, List]:
        """Mock query operation."""
        # Simple mock: return documents based on filters
        results = list(self.documents.values())
        
        # Apply where filter
        if where:
            filtered_results = []
            for doc in results:
                metadata = doc["metadata"]
                matches = True
                
                for key, value in where.items():
                    if key not in metadata:
                        matches = False
                        break
                    
                    if isinstance(value, dict) and "$in" in value:
                        if metadata[key] not in value["$in"]:
                            matches = False
                            break
                    elif metadata[key] != value:
                        matches = False
                        break
                
                if matches:
                    filtered_results.append(doc)
            
            results = filtered_results
        
        # Limit results
        results = results[:n_results]
        
        # Calculate mock distances (random but consistent)
        distances = []
        for i, doc in enumerate(results):
            # Mock distance calculation
            distance = 0.1 + (i * 0.1)  # Increasing distance
            distances.append(distance)
        
        return {
            "ids": [[doc["id"] for doc in results]],
            "documents": [[doc["document"] for doc in results]],
            "metadatas": [[doc["metadata"] for doc in results]],
            "distances": [distances],
            "embeddings": [[doc["embedding"] for doc in results]]
        }
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict] = None):
        """Mock delete operation."""
        if ids:
            for doc_id in ids:
                if doc_id in self.documents:
                    del self.documents[doc_id]
        
        if where:
            to_delete = []
            for doc_id, doc in self.documents.items():
                metadata = doc["metadata"]
                matches = True
                
                for key, value in where.items():
                    if key not in metadata or metadata[key] != value:
                        matches = False
                        break
                
                if matches:
                    to_delete.append(doc_id)
            
            for doc_id in to_delete:
                del self.documents[doc_id]
    
    def count(self) -> int:
        """Mock count operation."""
        return len(self.documents)


class MockChromaClient:
    """Mock ChromaDB client."""
    
    def __init__(self):
        self.collections = {}
    
    def create_collection(self, name: str, **kwargs) -> MockChromaCollection:
        """Mock collection creation."""
        collection = MockChromaCollection(name)
        self.collections[name] = collection
        return collection
    
    def get_collection(self, name: str) -> MockChromaCollection:
        """Mock get collection."""
        if name not in self.collections:
            raise ValueError(f"Collection {name} not found")
        return self.collections[name]
    
    def delete_collection(self, name: str):
        """Mock delete collection."""
        if name in self.collections:
            del self.collections[name]
    
    def list_collections(self) -> List[Dict[str, str]]:
        """Mock list collections."""
        return [{"name": name} for name in self.collections.keys()]
    
    def heartbeat(self):
        """Mock heartbeat."""
        return True


class ChromaDBMocker:
    """Utility class for mocking ChromaDB operations."""
    
    @staticmethod
    def create_mock_client() -> MockChromaClient:
        """Create a mocked ChromaDB client."""
        return MockChromaClient()
    
    @staticmethod
    def create_sample_documents() -> List[Dict[str, Any]]:
        """Create sample documents for testing."""
        return [
            {
                "id": "doc_1_chunk_0",
                "content": "Introduction to machine learning and artificial intelligence.",
                "metadata": {
                    "user_id": 1,
                    "document_id": 1,
                    "chunk_index": 0,
                    "page": 1,
                    "source": "test_document.pdf"
                },
                "embedding": [0.1] * 1536
            },
            {
                "id": "doc_1_chunk_1", 
                "content": "Supervised learning involves training models with labeled data.",
                "metadata": {
                    "user_id": 1,
                    "document_id": 1,
                    "chunk_index": 1,
                    "page": 1,
                    "source": "test_document.pdf"
                },
                "embedding": [0.2] * 1536
            },
            {
                "id": "doc_2_chunk_0",
                "content": "Natural language processing deals with text and speech.",
                "metadata": {
                    "user_id": 1,
                    "document_id": 2,
                    "chunk_index": 0,
                    "page": 1,
                    "source": "nlp_guide.pdf"
                },
                "embedding": [0.3] * 1536
            }
        ]
    
    @staticmethod
    def populate_mock_collection(collection: MockChromaCollection, documents: Optional[List[Dict]] = None):
        """Populate a mock collection with sample data."""
        if documents is None:
            documents = ChromaDBMocker.create_sample_documents()
        
        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        embeddings = [doc["embedding"] for doc in documents]
        
        collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    @staticmethod
    def mock_vector_search_results(query: str, k: int = 5) -> Dict[str, List]:
        """Generate mock vector search results."""
        # Create mock results based on query
        mock_docs = ChromaDBMocker.create_sample_documents()[:k]
        
        # Simulate relevance scoring
        results = []
        for i, doc in enumerate(mock_docs):
            score = 0.9 - (i * 0.1)  # Decreasing relevance
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": score,
                "distance": 1.0 - score
            })
        
        return {
            "ids": [[r["id"] for r in results]],
            "documents": [[r["content"] for r in results]],
            "metadatas": [[r["metadata"] for r in results]],
            "distances": [[r["distance"] for r in results]]
        }


# Convenience functions for pytest fixtures
def get_mock_chroma_client():
    """Get mocked ChromaDB client for testing."""
    return ChromaDBMocker.create_mock_client()


def get_populated_mock_collection(name: str = "test_collection"):
    """Get a mock collection populated with sample data."""
    collection = MockChromaCollection(name)
    ChromaDBMocker.populate_mock_collection(collection)
    return collection


