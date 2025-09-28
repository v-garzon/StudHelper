from sqlalchemy.orm import Session
from app.models import ChatSession, ChatMessage, UsageRecord
from app.schemas import ChatSessionCreate, ChatSessionResponse, MessageResponse, ChatResponse
from app.services.openai_service import OpenAIService
from app.services.permission_service import PermissionService
from app.services.usage_service import UsageService
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def create_session(self, db: Session, user_id: int, session_data: ChatSessionCreate) -> ChatSessionResponse:
        """Create a new chat session"""
        new_session = ChatSession(
            title=session_data.title,
            user_id=user_id,
            class_id=session_data.class_id
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        result = ChatSessionResponse.model_validate(new_session)
        result.message_count = 0
        
        return result
    
    async def send_message(self, db: Session, session: ChatSession, content: str, user_id: int) -> ChatResponse:
        """Send a message and get AI response"""
        start_time = time.time()
        
        try:
            # Create user message
            user_message = ChatMessage(
                session_id=session.id,
                content=content,
                is_user=True,
                timestamp=datetime.utcnow()
            )
            db.add(user_message)
            db.flush()
            
            # Get context from documents
            context = await self._get_context_for_session(db, session)
            
            # Get AI response
            ai_content, tokens_used = await self.openai_service.generate_response(content, context)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Create AI message
            ai_message = ChatMessage(
                session_id=session.id,
                content=ai_content,
                is_user=False,
                timestamp=datetime.utcnow(),
                response_time_ms=response_time_ms,
                context_used=context[:500] if context else None,  # Store first 500 chars
                tokens_used=tokens_used
            )
            db.add(ai_message)
            
            # Update session timestamp
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(user_message)
            db.refresh(ai_message)
            
            # Record usage and billing
            await self._record_usage(db, session, user_id, tokens_used)
            
            # Record token usage for limits
            permission_service = PermissionService()
            await permission_service.record_token_usage(db, user_id, session.class_id, tokens_used)
            
            return ChatResponse(
                user_message=MessageResponse.model_validate(user_message),
                ai_response=MessageResponse.model_validate(ai_message),
                cost=self._calculate_cost(tokens_used),
                response_time_ms=response_time_ms,
                context_provided=bool(context)
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in send_message: {e}")
            raise
    
    async def _get_context_for_session(self, db: Session, session: ChatSession) -> str:
        """Get relevant document context for the session"""
        try:
            from app.models import Document, DocumentChunk, DocumentScope
            
            context_chunks = []
            
            # Get class-level documents
            class_documents = db.query(Document).filter(
                Document.class_id == session.class_id,
                Document.scope == DocumentScope.CLASS,
                Document.processing_status == "completed"
            ).all()
            
            for doc in class_documents:
                chunks = db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == doc.id
                ).limit(3).all()  # Get top 3 chunks per document
                
                for chunk in chunks:
                    context_chunks.append(f"[{doc.original_filename}]: {chunk.content}")
            
            # Get session-specific documents
            session_documents = db.query(Document).filter(
                Document.session_id == session.id,
                Document.scope == DocumentScope.CHAT,
                Document.processing_status == "completed"
            ).all()
            
            for doc in session_documents:
                chunks = db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == doc.id
                ).limit(5).all()  # More chunks for session-specific docs
                
                for chunk in chunks:
                    context_chunks.append(f"[{doc.original_filename}]: {chunk.content}")
            
            # Combine context (limit to ~4000 chars to leave room for message)
            context = "\n\n".join(context_chunks)
            if len(context) > 4000:
                context = context[:4000] + "..."
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return ""
    
    async def _record_usage(self, db: Session, session: ChatSession, user_id: int, tokens_used: int):
        """Record usage for billing purposes"""
        try:
            # Determine billing
            permission_service = PermissionService()
            billed_user_id, is_sponsored, is_overflow = await permission_service.determine_billing(
                db, user_id, session.class_id
            )
            
            # Calculate cost
            cost = self._calculate_cost(tokens_used)
            
            # Create usage record
            usage_record = UsageRecord(
                user_id=user_id,
                model_name="gpt-4o-mini",
                operation_type="chat",
                input_tokens=int(tokens_used * 0.7),  # Rough estimate
                output_tokens=int(tokens_used * 0.3),
                cost=cost,
                session_id=session.id,
                billed_to_user_id=billed_user_id,
                is_sponsored=is_sponsored,
                is_overflow=is_overflow
            )
            
            db.add(usage_record)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost based on tokens used"""
        from app.config import get_settings
        settings = get_settings()
        
        # GPT-4o-mini pricing: $0.15/$0.60 per million tokens
        input_tokens = int(tokens_used * 0.7)
        output_tokens = int(tokens_used * 0.3)
        
        pricing = settings.OPENAI_PRICING["gpt-4o-mini"]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)

