import openai
from app.config import get_settings
import logging
import tiktoken

settings = get_settings()
logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

class OpenAIService:
    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.encoding = tiktoken.encoding_for_model(self.model)
    
    async def generate_response(self, user_message: str, context: str = None) -> tuple[str, int]:
        """Generate AI response using GPT-4o-mini"""
        try:
            # Prepare messages
            messages = []
            
            # System message
            system_message = """You are StudHelper, an AI assistant designed to help students learn from uploaded course materials. 
            You provide clear, educational explanations and help students understand complex topics.
            
            When answering:
            1. Be educational and supportive
            2. Reference the provided context when relevant
            3. Break down complex concepts into understandable parts
            4. Encourage further learning and questions
            """
            
            if context:
                system_message += f"\n\nRelevant course materials:\n{context}"
            
            messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": user_message})
            
            # Make API call
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            # Extract response
            ai_response = response.choices[0].message.content.strip()
            
            # Calculate tokens used
            total_tokens = response.usage.total_tokens
            
            return ai_response, total_tokens
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Return fallback response
            return "I apologize, but I'm experiencing technical difficulties. Please try again later.", 50
    
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for text chunks"""
        try:
            response = await openai.Embedding.acreate(
                model=settings.EMBEDDING_MODEL,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return 0

