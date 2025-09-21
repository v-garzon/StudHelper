"""OpenAI API mocking utilities for tests."""

from typing import Dict, Any, List, Optional, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import json
import time


class MockOpenAIResponse:
    """Mock OpenAI API response."""
    
    def __init__(self, content: str, model: str = "gpt-4o-mini", usage: Optional[Dict] = None):
        self.choices = [
            MagicMock(
                message=MagicMock(content=content),
                finish_reason="stop"
            )
        ]
        self.model = model
        self.usage = usage or {
            "prompt_tokens": 50,
            "completion_tokens": 20, 
            "total_tokens": 70
        }
        self.created = int(time.time())
        self.id = f"chatcmpl-test-{int(time.time())}"


class MockOpenAIStreamChunk:
    """Mock OpenAI streaming response chunk."""
    
    def __init__(self, content: str, finish_reason: Optional[str] = None):
        self.choices = [
            MagicMock(
                delta=MagicMock(content=content),
                finish_reason=finish_reason
            )
        ]


class MockEmbeddingResponse:
    """Mock OpenAI embedding response."""
    
    def __init__(self, embeddings: List[List[float]], usage: Optional[Dict] = None):
        self.data = [
            MagicMock(embedding=embedding) for embedding in embeddings
        ]
        self.usage = MagicMock(
            prompt_tokens=usage.get("prompt_tokens", 10) if usage else 10,
            total_tokens=usage.get("total_tokens", 10) if usage else 10
        )
        self.model = "text-embedding-3-large"


class OpenAIMocker:
    """Utility class for mocking OpenAI API calls."""
    
    @staticmethod
    def mock_chat_completion(
        content: str = "This is a mock AI response for testing.",
        model: str = "gpt-4o-mini",
        usage: Optional[Dict] = None
    ) -> MockOpenAIResponse:
        """Create mock chat completion response."""
        return MockOpenAIResponse(content, model, usage)
    
    @staticmethod
    def mock_streaming_response(
        content: str = "This is a mock streaming response.",
        chunk_size: int = 5
    ) -> List[MockOpenAIStreamChunk]:
        """Create mock streaming response chunks."""
        chunks = []
        words = content.split()
        
        for i in range(0, len(words), chunk_size):
            chunk_content = " ".join(words[i:i + chunk_size])
            if i + chunk_size < len(words):
                chunk_content += " "
            chunks.append(MockOpenAIStreamChunk(chunk_content))
        
        # Final chunk with finish reason
        chunks.append(MockOpenAIStreamChunk("", "stop"))
        return chunks
    
    @staticmethod
    def mock_embedding_response(
        num_embeddings: int = 1,
        embedding_dim: int = 1536,
        usage: Optional[Dict] = None
    ) -> MockEmbeddingResponse:
        """Create mock embedding response."""
        embeddings = [
            [0.1 * i] * embedding_dim for i in range(num_embeddings)
        ]
        return MockEmbeddingResponse(embeddings, usage)
    
    @staticmethod
    def create_mock_client() -> AsyncMock:
        """Create a fully mocked OpenAI client."""
        mock_client = AsyncMock()
        
        # Mock chat completions
        mock_client.chat.completions.create = AsyncMock(
            return_value=OpenAIMocker.mock_chat_completion()
        )
        
        # Mock embeddings
        mock_client.embeddings.create = AsyncMock(
            return_value=OpenAIMocker.mock_embedding_response()
        )
        
        # Mock audio transcriptions
        mock_client.audio.transcriptions.create = AsyncMock(
            return_value=MagicMock(
                text="This is a mock transcription of the audio file.",
                segments=[
                    {
                        "start": 0.0,
                        "end": 5.0,
                        "text": "This is a mock transcription"
                    },
                    {
                        "start": 5.0, 
                        "end": 10.0,
                        "text": "of the audio file."
                    }
                ]
            )
        )
        
        return mock_client


class MockOpenAIService:
    """Mock implementation of OpenAI service for testing."""
    
    def __init__(self):
        self.responses = {
            "economic": "This is a concise response from the economic model.",
            "standard": "This is a detailed response from the standard model with examples and explanations.",
            "turbo": "This is a comprehensive step-by-step response from the turbo model:\n1. First, let me analyze the question\n2. Then I'll break down the components\n3. Finally, I'll provide a synthesis"
        }
    
    async def create_completion(self, messages: List[Dict], mode: str = "economic", **kwargs) -> MockOpenAIResponse:
        """Mock chat completion."""
        content = self.responses.get(mode, self.responses["economic"])
        
        # Add context from the last user message
        user_message = messages[-1].get("content", "")
        if "math" in user_message.lower():
            content = f"Here's how to solve this math problem: {content}"
        elif "explain" in user_message.lower():
            content = f"Let me explain this concept: {content}"
        
        return MockOpenAIResponse(
            content=content,
            model="gpt-4o-mini" if mode == "economic" else "gpt-4o",
            usage={
                "prompt_tokens": len(" ".join(msg.get("content", "") for msg in messages)) // 4,
                "completion_tokens": len(content) // 4,
                "total_tokens": (len(" ".join(msg.get("content", "") for msg in messages)) + len(content)) // 4
            }
        )
    
    async def create_streaming_completion(self, messages: List[Dict], mode: str = "economic", **kwargs) -> AsyncGenerator[str, None]:
        """Mock streaming completion."""
        content = self.responses.get(mode, self.responses["economic"])
        words = content.split()
        
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
    
    def count_tokens(self, messages: List[Dict], model: str) -> int:
        """Mock token counting."""
        total_content = " ".join(msg.get("content", "") for msg in messages)
        return len(total_content) // 4  # Rough approximation
    
    def count_string_tokens(self, text: str, model: str) -> int:
        """Mock string token counting.""" 
        return len(text) // 4


# Convenience functions for pytest fixtures
def get_mock_openai_client():
    """Get mocked OpenAI client for testing."""
    return OpenAIMocker.create_mock_client()


def get_mock_chat_responses():
    """Get sample chat responses for different modes."""
    return {
        "economic": OpenAIMocker.mock_chat_completion(
            "Quick answer: This is the solution.",
            "gpt-4o-mini",
            {"prompt_tokens": 30, "completion_tokens": 10, "total_tokens": 40}
        ),
        "standard": OpenAIMocker.mock_chat_completion(
            "Detailed explanation: Let me break this down step by step with examples.",
            "gpt-4o", 
            {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80}
        ),
        "turbo": OpenAIMocker.mock_chat_completion(
            "Comprehensive analysis: 1) First, I'll analyze... 2) Then I'll synthesize... 3) Finally, I'll conclude...",
            "gpt-4o",
            {"prompt_tokens": 70, "completion_tokens": 50, "total_tokens": 120}
        )
    }

