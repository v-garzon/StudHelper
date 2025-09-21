"""AI chat service."""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.models import ChatSession, ChatMessage
from src.ai.schemas import ChatMode, ChatMessageRequest, ChatMessageResponse, StreamingChunk
from src.ai.openai_client import OpenAIService
from src.ai.prompt_templates import PromptTemplates
from src.ai.cost_calculator import CostCalculator
from src.rag.service import RAGService
from src.usage.tracker import UsageTracker

logger = logging.getLogger(__name__)


class ChatService:
    """AI chat service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_service = OpenAIService()
        self.cost_calculator = CostCalculator()
        self.rag_service = RAGService(db)
        self.usage_tracker = UsageTracker()
    
    async def chat(
        self,
        request: ChatMessageRequest,
        user_id: int,
        stream: bool = False,
    ) -> ChatMessageResponse:
        """Handle chat request."""
        start_time = time.time()
        
        try:
            # Get or create chat session
            session = await self._get_or_create_session(
                user_id=user_id,
                session_id=request.session_id,
                mode=request.mode.value,
            )
            
            # Get conversation history
            conversation_history = await self._get_conversation_history(session.id)
            
            # Get context from RAG if requested
            context_data = {}
            if request.include_context:
                context_data = await self.rag_service.get_context_for_chat(
                    query=request.message,
                    user_id=user_id,
                    max_context_length=request.max_context_length,
                )
            
            # Build messages for AI
            messages = self._build_messages(
                request=request,
                conversation_history=conversation_history,
                context_data=context_data,
            )
            
            # Count input tokens
            input_tokens = self.openai_service.count_tokens(messages, request.mode.value)
            
            # Generate AI response
            response = await self.openai_service.create_completion(
                messages=messages,
                mode=request.mode.value,
            )
            
            # Process response
            content = response.choices[0].message.content
            model = response.model
            
            # Count output tokens and calculate cost
            output_tokens = self.openai_service.count_string_tokens(content, request.mode.value)
            cost_info = self.cost_calculator.calculate_cost(
                mode=request.mode.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            
            # Save messages to database
            await self._save_messages(
                session_id=session.id,
                user_id=user_id,
                user_message=request.message,
                ai_response=content,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost_info["total_cost"],
                context_data=context_data,
            )
            
            # Update session statistics
            await self._update_session_stats(
                session_id=session.id,
                tokens=input_tokens + output_tokens,
                cost=cost_info["total_cost"],
            )
            
            # Track usage
            await self.usage_tracker.track_usage(
                user_id=user_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost_info["total_cost"],
                endpoint="chat",
            )
            
            response_time = time.time() - start_time
            
            return ChatMessageResponse(
                content=content,
                mode=request.mode.value,
                model=model,
                session_id=session.id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost=cost_info["total_cost"],
                context_used=context_data.get("has_context", False),
                sources=context_data.get("sources", []),
                response_time=response_time,
                timestamp=time.time(),
            )
            
        except Exception as e:
            logger.error(f"Chat service error: {str(e)}")
            raise
    
    async def stream_chat(
        self,
        request: ChatMessageRequest,
        user_id: int,
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Handle streaming chat request."""
        try:
            # Get or create session (similar to regular chat)
            session = await self._get_or_create_session(
                user_id=user_id,
                session_id=request.session_id,
                mode=request.mode.value,
            )
            
            # Get conversation history and context
            conversation_history = await self._get_conversation_history(session.id)
            context_data = {}
            if request.include_context:
                context_data = await self.rag_service.get_context_for_chat(
                    query=request.message,
                    user_id=user_id,
                    max_context_length=request.max_context_length,
                )
            
            # Build messages
            messages = self._build_messages(
                request=request,
                conversation_history=conversation_history,
                context_data=context_data,
            )
            
            # Count input tokens
            input_tokens = self.openai_service.count_tokens(messages, request.mode.value)
            
            # Stream response
            collected_content = ""
            async for chunk in self.openai_service.create_streaming_completion(
                messages=messages,
                mode=request.mode.value,
            ):
                collected_content += chunk
                yield StreamingChunk(
                    delta=chunk,
                    session_id=session.id,
                )
            
            # Calculate final costs and save
            output_tokens = self.openai_service.count_string_tokens(collected_content, request.mode.value)
            cost_info = self.cost_calculator.calculate_cost(
                mode=request.mode.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            
            # Save to database
            await self._save_messages(
                session_id=session.id,
                user_id=user_id,
                user_message=request.message,
                ai_response=collected_content,
                model=self.openai_service.model_mapping[request.mode.value],
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost_info["total_cost"],
                context_data=context_data,
            )
            
            # Send final chunk with usage info
            yield StreamingChunk(
                delta="",
                session_id=session.id,
                finished=True,
                usage={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                },
                cost=cost_info["total_cost"],
            )
            
        except Exception as e:
            logger.error(f"Streaming chat error: {str(e)}")
            yield StreamingChunk(
                delta=f"Error: {str(e)}",
                finished=True,
            )
    
    async def get_chat_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's chat sessions."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        sessions = result.scalars().all()
        
        return [
            {
                "id": session.id,
                "title": session.title,
                "mode": session.mode,
                "message_count": session.message_count,
                "total_tokens": session.total_tokens,
                "total_cost": session.total_cost,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            }
            for session in sessions
        ]
    
    async def get_chat_history(self, session_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get chat history for a session."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user_id,
            )
            .order_by(ChatMessage.created_at.asc())
        )
        messages = result.scalars().all()
        
        return [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "model": message.model,
                "input_tokens": message.input_tokens,
                "output_tokens": message.output_tokens,
                "cost": message.cost,
                "sources": message.sources,
                "created_at": message.created_at,
            }
            for message in messages
        ]
    
    # Private methods
    
    async def _get_or_create_session(
        self,
        user_id: int,
        session_id: Optional[int],
        mode: str,
    ) -> ChatSession:
        """Get existing session or create new one."""
        if session_id:
            result = await self.db.execute(
                select(ChatSession).where(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id,
                )
            )
            session = result.scalar_one_or_none()
            if session:
                return session
        
        # Create new session
        session = ChatSession(
            user_id=user_id,
            mode=mode,
            title=f"Chat Session {mode.title()}",
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def _get_conversation_history(self, session_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history for context."""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit * 2)  # Get more to account for user/assistant pairs
        )
        messages = list(result.scalars().all())
        
        # Convert to OpenAI format and reverse to chronological order
        conversation = []
        for message in reversed(messages):
            conversation.append({
                "role": message.role,
                "content": message.content,
            })
        
        return conversation
    
    def _build_messages(
        self,
        request: ChatMessageRequest,
        conversation_history: List[Dict[str, str]],
        context_data: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Build message list for OpenAI API."""
        # System prompt
        system_prompt = PromptTemplates.get_system_prompt(
            mode=request.mode.value,
            context=context_data.get("context"),
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": request.message})
        
        return messages
    
    async def _save_messages(
        self,
        session_id: int,
        user_id: int,
        user_message: str,
        ai_response: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        context_data: Dict[str, Any],
    ):
        """Save user and AI messages to database."""
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=user_message,
        )
        
        # Save AI message
        ai_msg = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=ai_response,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            context_used=context_data.get("context", ""),
            sources=str(context_data.get("sources", [])),
        )
        
        self.db.add_all([user_msg, ai_msg])
        await self.db.commit()
    
    async def _update_session_stats(self, session_id: int, tokens: int, cost: float):
        """Update session statistics."""
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        session = result.scalar_one()
        
        session.message_count += 2  # User + AI message
        session.total_tokens += tokens
        session.total_cost += cost
        
        await self.db.commit()

