"""Cost calculator tests."""

import pytest
from src.ai.cost_calculator import CostCalculator


class TestCostCalculator:
    """Test cost calculation functionality."""
    
    def test_token_counting(self):
        """Test token counting functionality."""
        calculator = CostCalculator()
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        
        tokens = calculator.count_tokens(messages, "gpt-4o-mini")
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_cost_calculation_economic(self):
        """Test cost calculation for economic mode."""
        calculator = CostCalculator()
        
        result = calculator.calculate_cost(
            mode="economic",
            input_tokens=1000,
            output_tokens=500
        )
        
        assert result["mode"] == "economic"
        assert result["model"] == "gpt-4o-mini"
        assert result["input_tokens"] == 1000
        assert result["output_tokens"] == 500
        assert result["total_tokens"] == 1500
        assert result["total_cost"] > 0
        assert result["input_cost"] > 0
        assert result["output_cost"] > 0
    
    def test_cost_calculation_standard(self):
        """Test cost calculation for standard mode."""
        calculator = CostCalculator()
        
        result = calculator.calculate_cost(
            mode="standard", 
            input_tokens=1000,
            output_tokens=500
        )
        
        assert result["mode"] == "standard"
        assert result["model"] == "gpt-4o"
        assert result["total_cost"] > 0
        
        # Standard mode should be more expensive than economic
        economic_result = calculator.calculate_cost("economic", 1000, 500)
        assert result["total_cost"] > economic_result["total_cost"]
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        calculator = CostCalculator()
        
        estimated = calculator.estimate_cost("economic", 1500)
        assert estimated > 0
        assert isinstance(estimated, float)
    
    def test_mode_info(self):
        """Test getting mode information."""
        calculator = CostCalculator()
        
        info = calculator.get_mode_info("economic")
        assert info["mode"] == "economic"
        assert info["model"] == "gpt-4o-mini"
        assert "description" in info
        assert info["input_price_per_1m"] > 0

