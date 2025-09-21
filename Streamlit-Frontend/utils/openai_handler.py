

"""
OpenAI API Handler with 3 Chat Modes and Cost Tracking
Handles embeddings, chat completions, and token/cost monitoring
"""

import os
import openai
import tiktoken
import time
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIHandler:
    """Handles OpenAI API calls with cost tracking and multiple chat modes"""
    
    def __init__(self):
        """Initialize OpenAI client and cost tracking"""
        self.client = None
        self.initialize_client()
        
        # Model configurations and pricing (per 1M tokens)
        self.model_config = {
            'economic': {
                'model': 'gpt-4o-mini',
                'input_cost': 0.15,   # $0.15 per 1M input tokens
                'output_cost': 0.60,  # $0.60 per 1M output tokens
                'max_tokens': 4096,
                'temperature': 0.7,
                'description': 'Most cost-effective option'
            },
            'standard': {
                'model': 'gpt-4o',
                'input_cost': 2.50,   # $2.50 per 1M input tokens  
                'output_cost': 10.00, # $10.00 per 1M output tokens
                'max_tokens': 4096,
                'temperature': 0.7,
                'description': 'Balanced performance and cost'
            },
            'turbo': {
                'model': 'gpt-4o',
                'input_cost': 2.50,   # Same as standard but with CoT
                'output_cost': 10.00, 
                'max_tokens': 8192,   # More tokens for detailed responses
                'temperature': 0.3,   # Lower temp for more focused responses
                'description': 'Best performance with Chain of Thought'
            }
        }
        
        # Embedding model configuration
        self.embedding_config = {
            'small': {
                'model': 'text-embedding-3-small',
                'cost': 0.02,  # $0.02 per 1M tokens
                'dimensions': 1536,
                'description': 'Cost-effective embeddings'
            },
            'large': {
                'model': 'text-embedding-3-large', 
                'cost': 0.13,  # $0.13 per 1M tokens
                'dimensions': 3072,
                'description': 'Higher quality embeddings'
            }
        }
        
        # Initialize tokenizers
        self.tokenizers = {}
        self._initialize_tokenizers()
        
        # Initialize cost tracking
        if 'cost_tracking' not in st.session_state:
            st.session_state.cost_tracking = {
                'total_cost': 0.0,
                'session_cost': 0.0,
                'token_usage': {},
                'api_calls': 0,
                'last_reset': datetime.now().isoformat()
            }
    
    def initialize_client(self):
        """Initialize OpenAI client with API key"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                st.error("❌ OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
                st.stop()
            
            self.client = openai.OpenAI(api_key=api_key)
            
            # Test the connection
            self._test_connection()
            
        except Exception as e:
            st.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
            st.stop()
    
    def _test_connection(self):
        """Test OpenAI API connection"""
        try:
            # Simple test call
            response = self.client.models.list()
            logger.info("✅ OpenAI API connection successful")
        except Exception as e:
            logger.error(f"❌ OpenAI API connection failed: {str(e)}")
            raise e
    
    def _initialize_tokenizers(self):
        """Initialize tokenizers for different models"""
        try:
            self.tokenizers['gpt-4o'] = tiktoken.encoding_for_model('gpt-4o')
            self.tokenizers['gpt-4o-mini'] = tiktoken.encoding_for_model('gpt-4o-mini')
            # Use gpt-4o tokenizer for embedding models (close approximation)
            self.tokenizers['embedding'] = tiktoken.encoding_for_model('gpt-4o')
        except Exception as e:
            logger.warning(f"Could not load specific tokenizers, using cl100k_base: {e}")
            # Fallback tokenizer
            fallback = tiktoken.get_encoding("cl100k_base")
            self.tokenizers['gpt-4o'] = fallback
            self.tokenizers['gpt-4o-mini'] = fallback
            self.tokenizers['embedding'] = fallback
    
    def count_tokens(self, text: str, model: str = 'gpt-4o') -> int:
        """Count tokens in text for a specific model"""
        try:
            if model in ['text-embedding-3-small', 'text-embedding-3-large']:
                tokenizer = self.tokenizers.get('embedding')
            else:
                tokenizer = self.tokenizers.get(model, self.tokenizers.get('gpt-4o'))
            
            return len(tokenizer.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            # Rough approximation: 4 characters per token
            return len(text) // 4
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, mode: str) -> float:
        """Estimate cost for a chat completion"""
        config = self.model_config.get(mode, self.model_config['standard'])
        
        input_cost = (input_tokens / 1_000_000) * config['input_cost']
        output_cost = (output_tokens / 1_000_000) * config['output_cost']
        
        return input_cost + output_cost
    
    def estimate_embedding_cost(self, tokens: int, model_type: str = 'small') -> float:
        """Estimate cost for embedding generation"""
        config = self.embedding_config.get(model_type, self.embedding_config['small'])
        return (tokens / 1_000_000) * config['cost']
    
    def generate_embeddings(self, texts: List[str], model_type: str = 'small') -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        config = self.embedding_config[model_type]
        
        try:
            # Count tokens for cost estimation
            total_tokens = sum(self.count_tokens(text) for text in texts)
            estimated_cost = self.estimate_embedding_cost(total_tokens, model_type)
            
            # Generate embeddings
            response = self.client.embeddings.create(
                input=texts,
                model=config['model']
            )
            
            # Track usage and cost
            actual_tokens = response.usage.total_tokens
            actual_cost = self.estimate_embedding_cost(actual_tokens, model_type)
            
            self._track_usage('embedding', config['model'], actual_tokens, 0, actual_cost)
            
            # Extract embeddings
            embeddings = [embedding.embedding for embedding in response.data]
            
            logger.info(f"Generated {len(embeddings)} embeddings using {config['model']} (${actual_cost:.4f})")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise e
    
    def chat_completion(self, messages: List[Dict], mode: str = 'standard', stream: bool = False) -> Dict[str, Any]:
        """Generate chat completion with specified mode"""
        config = self.model_config[mode]
        
        try:
            # Add system message for turbo mode (Chain of Thought)
            if mode == 'turbo':
                messages = self._add_cot_system_message(messages)
            
            # Count input tokens
            input_text = self._messages_to_text(messages)
            input_tokens = self.count_tokens(input_text, config['model'])
            
            # Estimate cost
            estimated_output_tokens = config['max_tokens'] // 2  # Conservative estimate
            estimated_cost = self.estimate_cost(input_tokens, estimated_output_tokens, mode)
            
            # Make API call
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=config['model'],
                messages=messages,
                max_tokens=config['max_tokens'],
                temperature=config['temperature'],
                stream=stream
            )
            
            response_time = time.time() - start_time
            
            # Extract response details
            if stream:
                # Handle streaming response
                return self._handle_streaming_response(response, config, input_tokens, response_time)
            else:
                # Handle non-streaming response
                return self._handle_standard_response(response, config, input_tokens, response_time, mode)
                
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return {
                'content': f"Error: {str(e)}",
                'cost': 0.0,
                'tokens': {'input': input_tokens, 'output': 0},
                'mode': mode,
                'error': True
            }
    
    def _add_cot_system_message(self, messages: List[Dict]) -> List[Dict]:
        """Add Chain of Thought system message for turbo mode"""
        cot_system = {
            'role': 'system',
            'content': """You are an advanced AI tutor with Chain of Thought reasoning. For each response:

1. **Think Step by Step**: Break down complex problems into logical steps
2. **Show Your Reasoning**: Explain your thought process clearly
3. **Use Context Effectively**: Reference specific parts of the provided materials
4. **Be Thorough**: Provide comprehensive, detailed explanations
5. **Check Your Work**: Verify your reasoning and conclusions

When answering questions:
- First, identify the key concepts involved
- Then, work through the problem systematically
- Finally, provide a clear, complete answer
- Always cite your sources from the provided context"""
        }
        
        # Insert system message at the beginning
        return [cot_system] + messages
    
    def _messages_to_text(self, messages: List[Dict]) -> str:
        """Convert messages to text for token counting"""
        return '\n'.join([f"{msg['role']}: {msg['content']}" for msg in messages])
    
    def _handle_standard_response(self, response, config: Dict, input_tokens: int, response_time: float, mode: str) -> Dict[str, Any]:
        """Handle non-streaming response"""
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        
        actual_cost = self.estimate_cost(input_tokens, output_tokens, mode)
        
        # Track usage
        self._track_usage('chat', config['model'], input_tokens, output_tokens, actual_cost)
        
        content = response.choices[0].message.content
        
        result = {
            'content': content,
            'cost': actual_cost,
            'tokens': {
                'input': input_tokens,
                'output': output_tokens,
                'total': total_tokens
            },
            'mode': mode,
            'model': config['model'],
            'response_time': response_time,
            'error': False
        }
        
        logger.info(f"Chat completion ({mode}): ${actual_cost:.4f} | {total_tokens} tokens | {response_time:.1f}s")
        
        return result
    
    def _handle_streaming_response(self, response, config: Dict, input_tokens: int, response_time: float) -> Dict[str, Any]:
        """Handle streaming response (placeholder for future implementation)"""
        # For now, convert to non-streaming
        content_chunks = []
        for chunk in response:
            if chunk.choices[0].delta.content:
                content_chunks.append(chunk.choices[0].delta.content)
        
        content = ''.join(content_chunks)
        output_tokens = self.count_tokens(content, config['model'])
        
        return {
            'content': content,
            'cost': self.estimate_cost(input_tokens, output_tokens, 'standard'),
            'tokens': {'input': input_tokens, 'output': output_tokens},
            'response_time': response_time,
            'error': False
        }
    
    def _track_usage(self, operation_type: str, model: str, input_tokens: int, output_tokens: int, cost: float):
        """Track API usage and costs"""
        if 'cost_tracking' not in st.session_state:
            st.session_state.cost_tracking = {
                'total_cost': 0.0,
                'session_cost': 0.0,
                'token_usage': {},
                'api_calls': 0,
                'last_reset': datetime.now().isoformat()
            }
        
        # Update totals
        st.session_state.cost_tracking['total_cost'] += cost
        st.session_state.cost_tracking['session_cost'] += cost
        st.session_state.cost_tracking['api_calls'] += 1
        
        # Track by model
        if model not in st.session_state.cost_tracking['token_usage']:
            st.session_state.cost_tracking['token_usage'][model] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_cost': 0.0,
                'calls': 0
            }
        
        model_usage = st.session_state.cost_tracking['token_usage'][model]
        model_usage['input_tokens'] += input_tokens
        model_usage['output_tokens'] += output_tokens
        model_usage['total_cost'] += cost
        model_usage['calls'] += 1
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get current cost tracking summary"""
        tracking = st.session_state.get('cost_tracking', {})
        
        return {
            'session_cost': tracking.get('session_cost', 0.0),
            'total_cost': tracking.get('total_cost', 0.0),
            'api_calls': tracking.get('api_calls', 0),
            'token_usage': tracking.get('token_usage', {}),
            'last_reset': tracking.get('last_reset', 'Never')
        }
    
    def reset_session_costs(self):
        """Reset session cost tracking"""
        if 'cost_tracking' in st.session_state:
            st.session_state.cost_tracking['session_cost'] = 0.0
            st.session_state.cost_tracking['last_reset'] = datetime.now().isoformat()
    
    def get_available_modes(self) -> Dict[str, Dict]:
        """Get available chat modes with descriptions"""
        return self.model_config
    
    def get_embedding_options(self) -> Dict[str, Dict]:
        """Get available embedding options"""
        return self.embedding_config

# Utility functions for easy integration
def create_context_prompt(question: str, context_chunks: List[Dict], mode: str = 'standard') -> List[Dict]:
    """Create a prompt with context for RAG"""
    
    # Build context from chunks
    context_text = "\n\n".join([
        f"Source: {chunk.get('source', 'Document')}\nContent: {chunk.get('content', '')}"
        for chunk in context_chunks
    ])
    
    if mode == 'turbo':
        system_content = f"""You are an expert AI tutor with access to the student's study materials. Use the provided context to answer questions thoroughly and accurately.

CONTEXT MATERIALS:
{context_text}

Instructions:
1. Base your answers primarily on the provided context
2. Think through the problem step by step
3. Provide detailed explanations with examples
4. Cite specific sources when referencing information
5. If the context doesn't contain enough information, say so clearly
6. Make connections between different concepts when relevant"""

    else:
        system_content = f"""You are an AI tutor helping a student with their study materials. Use the provided context to answer their questions accurately.

CONTEXT MATERIALS:
{context_text}

Guidelines:
- Answer based on the provided materials
- Be clear and concise
- Cite your sources when possible
- If information isn't in the context, mention this limitation"""
    
    return [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': question}
    ]

def format_cost_display(cost: float) -> str:
    """Format cost for display"""
    if cost < 0.001:
        return f"${cost:.6f}"
    elif cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.3f}"

