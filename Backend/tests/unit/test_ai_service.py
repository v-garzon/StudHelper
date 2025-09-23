"""AI service tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.ai.service import ChatService
from src.ai.schemas import ChatMessageRequest, ChatMode
from src.ai.cost_calculator import CostCalculator


class TestCostCalculator:
    """Test cost calculation."""
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        calculator = CostCalculator()
        
        result = calculator.calculate_cost(
            mode="economic",
            input_tokens=100,
            output_tokens=50,
        )
        
        assert result["mode"] == "economic"
        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 50
        assert result["total_tokens"] == 150
        assert result["total_cost"] > 0
    
    def test_count_tokens(self):
        """Test token counting."""
        calculator = CostCalculator()
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        tokens = calculator.count_tokens(messages, "gpt-4o-mini")
        assert tokens > 0


class TestChatService:
    """Test chat service."""
    
    @pytest.mark.asyncio
    async def test_chat_without_context(self, db_session, test_user, mock_openai):
        """Test basic chat without context."""
        service = ChatService(db_session)
        
        request = ChatMessageRequest(
            message="Hello, how are you?",
            mode=ChatMode.ECONOMIC,
            include_context=False,
        )
        
        response = await service.chat(request, test_user.id)
        
        assert response.content == "Mock AI response"
        assert response.mode == "economic"
        assert response.model == "gpt-4o-mini"
        assert response.input_tokens > 0
        assert response.output_tokens > 0

