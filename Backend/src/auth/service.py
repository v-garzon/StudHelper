"""Authentication service."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_handler import create_access_token, hash_password, verify_password
from src.auth.models import User
from src.auth.schemas import LoginResponse, UserCreate, UserResponse, UserUpdate
from src.core.exceptions import AuthenticationError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValidationError("User with this email already exists")
        
        existing_username = await self.get_user_by_username(user_data.username)
        if existing_username:
            raise ValidationError("User with this username already exists")
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"Created user: {user.email}")
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()
        
        return user
    async def login(self, email: str, password: str) -> LoginResponse:
        """Login user and return token."""
        user = await self.authenticate_user(email, password)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        
        # Refresh the user object to ensure all attributes are loaded
        await self.db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Convert to dict first to avoid SQLAlchemy async issues
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
        }
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user_dict),
        )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Update fields
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        
        logger.info(f"Deleted user: {user.email}")
        return True

