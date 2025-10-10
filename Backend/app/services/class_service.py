from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, UploadFile
from app.models import Class, ClassMembership, Document, DocumentScope, User, ChatSession
from app.schemas.class_schemas import ClassCreate, ClassUpdate, ClassResponse, ClassDetailResponse
from typing import List, Optional, Dict
import random
import string
import logging

logger = logging.getLogger(__name__)


class ClassService:
    
    @staticmethod
    def generate_class_code() -> str:
        """Generate unique 8-character class code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    @staticmethod
    async def create_class(
        db: Session,
        name: str,
        description: Optional[str],
        owner_id: int,
        files: Optional[List[UploadFile]] = None,
        file_descriptions: Optional[Dict[str, str]] = None,
        youtube_urls: Optional[List[str]] = None,
        youtube_descriptions: Optional[List[str]] = None
    ) -> ClassDetailResponse:
        """Create new class with optional documents"""
        
        try:
            # 1. Generate unique class code
            max_attempts = 10
            class_code = None
            for _ in range(max_attempts):
                potential_code = ClassService.generate_class_code()
                existing = db.query(Class).filter(Class.class_code == potential_code).first()
                if not existing:
                    class_code = potential_code
                    break
            
            if not class_code:
                raise HTTPException(status_code=500, detail="Failed to generate unique class code")
            
            # 2. Create class
            new_class = Class(
                name=name,
                description=description,
                class_code=class_code,
                owner_id=owner_id
            )
            db.add(new_class)
            db.flush()
            
            logger.info(f"Created class {new_class.id} with code {class_code}")
            
            # 3. Create owner membership
            owner_membership = ClassMembership(
                user_id=owner_id,
                class_id=new_class.id,
                is_manager=True,
                can_chat=True,
                daily_token_limit=100000,
                is_sponsored=True
            )
            db.add(owner_membership)
            
            # 4. Process file uploads (placeholder - full implementation in Phase 3)
            documents = []
            if files:
                for file in files:
                    description = file_descriptions.get(file.filename, '') if file_descriptions else ''
                    
                    # Simple file validation
                    if file.size > 10 * 1024 * 1024:  # 10MB limit
                        logger.warning(f"File {file.filename} exceeds size limit")
                        continue
                    
                    document = Document(
                        filename=file.filename,
                        original_filename=file.filename,
                        file_path=f"uploads/{new_class.id}/{file.filename}",
                        file_type=file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown',
                        file_size=file.size or 0,
                        description=description,
                        scope=DocumentScope.CLASS,
                        class_id=new_class.id,
                        uploaded_by=owner_id
                    )
                    db.add(document)
                    documents.append(document)
                    
                    logger.info(f"Added document {file.filename} to class {new_class.id}")
            
            # 5. Process YouTube videos
            if youtube_urls:
                for i, url in enumerate(youtube_urls):
                    description = youtube_descriptions[i] if youtube_descriptions and i < len(youtube_descriptions) else ''
                    video_id = ClassService._extract_youtube_id(url)
                    
                    document = Document(
                        filename=f"YouTube: {video_id}",
                        original_filename=url,
                        file_path="",
                        file_type="youtube",
                        file_size=0,
                        description=description,
                        url=url,
                        scope=DocumentScope.CLASS,
                        class_id=new_class.id,
                        uploaded_by=owner_id
                    )
                    db.add(document)
                    documents.append(document)
                    
                    logger.info(f"Added YouTube video {video_id} to class {new_class.id}")
            
            db.commit()
            db.refresh(new_class)
            
            # Refresh documents to get IDs
            for doc in documents:
                db.refresh(doc)
            
            # Build response
            response = ClassDetailResponse(
                id=new_class.id,
                name=new_class.name,
                description=new_class.description,
                class_code=new_class.class_code,
                owner_id=new_class.owner_id,
                created_at=new_class.created_at,
                is_owner=True,
                chat_session_count=0,
                document_count=len(documents),
                member_count=1,
                documents=[
                    {
                        "id": doc.id,
                        "filename": doc.filename,
                        "original_filename": doc.original_filename,
                        "file_type": doc.file_type,
                        "file_size": doc.file_size,
                        "description": doc.description,
                        "url": doc.url,
                        "uploaded_at": doc.uploaded_at,
                        "processing_status": doc.processing_status.value
                    }
                    for doc in documents
                ]
            )
            
            return response
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating class: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create class: {str(e)}")
    
    @staticmethod
    def get_user_classes(db: Session, user_id: int) -> List[ClassResponse]:
        """Get all classes user is member of"""
        
        try:
            # Get memberships
            memberships = db.query(ClassMembership).filter(
                ClassMembership.user_id == user_id
            ).all()
            
            classes = []
            for membership in memberships:
                class_obj = db.query(Class).filter(Class.id == membership.class_id).first()
                if not class_obj:
                    continue
                
                # Count chat sessions
                chat_count = db.query(func.count(ChatSession.id)).filter(
                    ChatSession.class_id == class_obj.id
                ).scalar() or 0
                
                # Count documents
                doc_count = db.query(func.count(Document.id)).filter(
                    Document.class_id == class_obj.id,
                    Document.scope == DocumentScope.CLASS
                ).scalar() or 0
                
                # Count members
                member_count = db.query(func.count(ClassMembership.id)).filter(
                    ClassMembership.class_id == class_obj.id
                ).scalar() or 0
                
                class_response = ClassResponse(
                    id=class_obj.id,
                    name=class_obj.name,
                    description=class_obj.description,
                    class_code=class_obj.class_code,
                    owner_id=class_obj.owner_id,
                    created_at=class_obj.created_at,
                    is_owner=class_obj.owner_id == user_id,
                    chat_session_count=chat_count,
                    document_count=doc_count,
                    member_count=member_count
                )
                classes.append(class_response)
            
            return classes
            
        except Exception as e:
            logger.error(f"Error fetching user classes: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch classes")
    
    @staticmethod
    def get_class_details(db: Session, class_id: int, user_id: int) -> ClassDetailResponse:
        """Get detailed class information with documents"""
        
        try:
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            if not class_obj:
                raise HTTPException(status_code=404, detail="Class not found")
            
            # Check membership
            membership = db.query(ClassMembership).filter(
                ClassMembership.class_id == class_id,
                ClassMembership.user_id == user_id
            ).first()
            
            if not membership:
                raise HTTPException(status_code=403, detail="Not a member of this class")
            
            # Get documents
            documents = db.query(Document).filter(
                Document.class_id == class_id,
                Document.scope == DocumentScope.CLASS
            ).order_by(Document.uploaded_at.desc()).all()
            
            # Count sessions and members
            chat_count = db.query(func.count(ChatSession.id)).filter(
                ChatSession.class_id == class_id
            ).scalar() or 0
            
            member_count = db.query(func.count(ClassMembership.id)).filter(
                ClassMembership.class_id == class_id
            ).scalar() or 0
            
            response = ClassDetailResponse(
                id=class_obj.id,
                name=class_obj.name,
                description=class_obj.description,
                class_code=class_obj.class_code,
                owner_id=class_obj.owner_id,
                created_at=class_obj.created_at,
                is_owner=class_obj.owner_id == user_id,
                chat_session_count=chat_count,
                document_count=len(documents),
                member_count=member_count,
                documents=[
                    {
                        "id": doc.id,
                        "filename": doc.filename,
                        "original_filename": doc.original_filename,
                        "file_type": doc.file_type,
                        "file_size": doc.file_size,
                        "description": doc.description,
                        "url": doc.url,
                        "uploaded_at": doc.uploaded_at,
                        "processing_status": doc.processing_status.value
                    }
                    for doc in documents
                ]
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching class details: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch class details")
    
    @staticmethod
    def update_class(
        db: Session,
        class_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> ClassResponse:
        """Update class information (owner only)"""
        
        try:
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            if not class_obj:
                raise HTTPException(status_code=404, detail="Class not found")
            
            if class_obj.owner_id != user_id:
                raise HTTPException(status_code=403, detail="Only owner can update class")
            
            if name is not None:
                class_obj.name = name
            if description is not None:
                class_obj.description = description
            
            db.commit()
            db.refresh(class_obj)
            
            # Get counts for response
            chat_count = db.query(func.count(ChatSession.id)).filter(
                ChatSession.class_id == class_id
            ).scalar() or 0
            
            doc_count = db.query(func.count(Document.id)).filter(
                Document.class_id == class_id,
                Document.scope == DocumentScope.CLASS
            ).scalar() or 0
            
            member_count = db.query(func.count(ClassMembership.id)).filter(
                ClassMembership.class_id == class_id
            ).scalar() or 0
            
            return ClassResponse(
                id=class_obj.id,
                name=class_obj.name,
                description=class_obj.description,
                class_code=class_obj.class_code,
                owner_id=class_obj.owner_id,
                created_at=class_obj.created_at,
                is_owner=True,
                chat_session_count=chat_count,
                document_count=doc_count,
                member_count=member_count
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating class: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update class")
    
    @staticmethod
    def delete_class(db: Session, class_id: int, user_id: int):
        """Delete class and all related data (owner only)"""
        
        try:
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            if not class_obj:
                raise HTTPException(status_code=404, detail="Class not found")
            
            if class_obj.owner_id != user_id:
                raise HTTPException(status_code=403, detail="Only owner can delete class")
            
            logger.info(f"Deleting class {class_id} by user {user_id}")
            
            # Delete all related records (CASCADE should handle most)
            # But we'll be explicit for important ones
            
            # Delete documents
            db.query(Document).filter(Document.class_id == class_id).delete()
            
            # Delete memberships
            db.query(ClassMembership).filter(ClassMembership.class_id == class_id).delete()
            
            # Delete chat sessions (and CASCADE will handle messages)
            db.query(ChatSession).filter(ChatSession.class_id == class_id).delete()
            
            # Delete class
            db.delete(class_obj)
            
            db.commit()
            
            logger.info(f"Successfully deleted class {class_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting class: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete class")
    
    @staticmethod
    def _extract_youtube_id(url: str) -> str:
        """Extract video ID from YouTube URL"""
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif 'watch?v=' in url:
            return url.split('watch?v=')[1].split('&')[0]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1].split('?')[0]
        return url


