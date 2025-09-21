"""OpenAI client integration."""

import asyncio
import logging
from typing import List, Dict, Any, AsyncGenerator

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings
from src.core.exceptions import ExternalServiceError
from src.ai.cost_calculator import CostCalculator

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIService:
    """OpenAI integration service."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            organization=settings.OPENAI_ORG_ID,
        )
        self.cost_calculator = CostCalculator()
        
        self.model_mapping = {
            'economic': 'gpt-4o-mini',
            'standard': 'gpt-4o',
            'turbo': 'gpt-4o',
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        mode: str = "economic",
        stream: bool = False,
        **kwargs
    ) -> Any:
        """Create chat completion with automatic retry."""
        model = self.model_mapping.get(mode, 'gpt-4o-mini')
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                temperature=0.1 if mode == 'turbo' else 0.7,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise ExternalServiceError(f"AI service error: {str(e)}", "OpenAI")
    
    async def create_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        mode: str = "economic",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Create streaming chat completion."""
        model = self.model_mapping.get(mode, 'gpt-4o-mini')
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.1 if mode == 'turbo' else 0.7,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"Error: {str(e)}"
    
    def count_tokens(self, messages: List[Dict[str, str]], mode: str) -> int:
        """Count tokens in messages."""
        model = self.model_mapping.get(mode, 'gpt-4o-mini')
        return self.cost_calculator.count_tokens(messages, model)
    
    def count_string_tokens(self, text: str, mode: str) -> int:
        """Count tokens in a string."""
        model = self.model_mapping.get(mode, 'gpt-4o-mini')
        return self.cost_calculator.count_string_tokens(text, model)

