"""Token counting and cost calculation."""

import logging
from typing import Dict, List, Any

import tiktoken

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CostCalculator:
    """Token counting and cost calculation service."""
    
    def __init__(self):
        self.encodings = {
            'gpt-4o-mini': tiktoken.encoding_for_model('gpt-4o-mini'),
            'gpt-4o': tiktoken.encoding_for_model('gpt-4o'),
        }
        
        self.pricing = {
            'economic': {
                'input': settings.ECONOMIC_INPUT_PRICE / 1_000_000,  # Per token
                'output': settings.ECONOMIC_OUTPUT_PRICE / 1_000_000,
                'model': 'gpt-4o-mini',
            },
            'standard': {
                'input': settings.STANDARD_INPUT_PRICE / 1_000_000,
                'output': settings.STANDARD_OUTPUT_PRICE / 1_000_000,
                'model': 'gpt-4o',
            },
            'turbo': {
                'input': settings.STANDARD_INPUT_PRICE / 1_000_000,
                'output': settings.STANDARD_OUTPUT_PRICE / 1_000_000,
                'model': 'gpt-4o',
            },
        }
    
    def count_tokens(self, messages: List[Dict[str, str]], model: str) -> int:
        """Count tokens in messages using tiktoken."""
        encoding = self.encodings.get(model, self.encodings['gpt-4o-mini'])
        
        tokens = 0
        for message in messages:
            tokens += 3  # Message formatting tokens
            for key, value in message.items():
                tokens += len(encoding.encode(str(value)))
                if key == "name":
                    tokens -= 1
        tokens += 3  # Assistant reply priming
        return tokens
    
    def count_string_tokens(self, text: str, model: str) -> int:
        """Count tokens in a string."""
        encoding = self.encodings.get(model, self.encodings['gpt-4o-mini'])
        return len(encoding.encode(text))
    
    def calculate_cost(
        self,
        mode: str,
        input_tokens: int,
        output_tokens: int,
    ) -> Dict[str, float]:
        """Calculate cost for token usage."""
        if mode not in self.pricing:
            raise ValueError(f"Unknown mode: {mode}")
        
        pricing = self.pricing[mode]
        
        input_cost = input_tokens * pricing['input']
        output_cost = output_tokens * pricing['output']
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'mode': mode,
            'model': pricing['model'],
        }
    
    def estimate_cost(self, mode: str, estimated_tokens: int) -> float:
        """Estimate cost for a given number of tokens."""
        if mode not in self.pricing:
            return 0.0
        
        pricing = self.pricing[mode]
        # Use average of input and output pricing for estimation
        avg_price = (pricing['input'] + pricing['output']) / 2
        return estimated_tokens * avg_price
    
    def get_mode_info(self, mode: str) -> Dict[str, Any]:
        """Get information about a specific mode."""
        if mode not in self.pricing:
            return {}
        
        pricing = self.pricing[mode]
        return {
            'mode': mode,
            'model': pricing['model'],
            'input_price_per_1m': pricing['input'] * 1_000_000,
            'output_price_per_1m': pricing['output'] * 1_000_000,
            'description': self._get_mode_description(mode),
        }
    
    def _get_mode_description(self, mode: str) -> str:
        """Get description for a mode."""
        descriptions = {
            'economic': 'Fast, cost-effective responses for basic questions',
            'standard': 'Detailed explanations with examples and context',
            'turbo': 'Advanced reasoning with step-by-step thinking',
        }
        return descriptions.get(mode, '')

