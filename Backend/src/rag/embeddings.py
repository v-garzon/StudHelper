"""Embedding generation service."""

import asyncio
import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings
from src.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    """Embedding generation service."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            organization=settings.OPENAI_ORG_ID,
        )
        self.model = "text-embedding-3-large"
        self.batch_size = 100  # OpenAI's batch limit
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return {"embeddings": [], "usage": {"total_tokens": 0}}
        
        try:
            # Process in batches
            all_embeddings = []
            total_tokens = 0
            
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                batch_result = await self._generate_batch_embeddings(batch)
                
                all_embeddings.extend(batch_result["embeddings"])
                total_tokens += batch_result["usage"]["total_tokens"]
            
            return {
                "embeddings": all_embeddings,
                "usage": {"total_tokens": total_tokens},
                "model": self.model,
            }
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            raise ExternalServiceError(f"Failed to generate embeddings: {str(e)}", "OpenAI")
    
    async def _generate_batch_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """Generate embeddings for a batch of texts."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        
        embeddings = [embedding.embedding for embedding in response.data]
        
        return {
            "embeddings": embeddings,
            "usage": response.usage.model_dump(),
        }
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        result = await self.generate_embeddings([text])
        return result["embeddings"][0]
    
    def preprocess_text_for_embedding(self, text: str) -> str:
        """Preprocess text for optimal embedding generation."""
        # Clean text
        text = text.strip()
        
        # Truncate if too long (OpenAI has token limits)
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = 32000  # Conservative estimate for 8k token limit
        if len(text) > max_chars:
            text = text[:max_chars]
            # Try to end at a sentence boundary
            last_period = text.rfind('. ')
            if last_period > max_chars * 0.8:  # If we can find a period in the last 20%
                text = text[:last_period + 1]
        
        return text

