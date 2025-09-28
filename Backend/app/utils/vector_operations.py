import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class VectorOperations:
    """Simple vector operations for document similarity search"""
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_vector: List[float], vectors: Dict[str, List[float]], top_k: int = 5) -> List[str]:
        """Find the most similar vectors to the query vector"""
        try:
            similarities = []
            
            for key, vector in vectors.items():
                similarity = self.cosine_similarity(query_vector, vector)
                similarities.append((key, similarity))
            
            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [key for key, _ in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Error finding similar vectors: {e}")
            return []
    
    def average_vectors(self, vectors: List[List[float]]) -> List[float]:
        """Calculate the average of multiple vectors"""
        try:
            if not vectors:
                return []
            
            vectors_array = np.array(vectors)
            average = np.mean(vectors_array, axis=0)
            return average.tolist()
            
        except Exception as e:
            logger.error(f"Error averaging vectors: {e}")
            return []

