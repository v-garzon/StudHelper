from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class AuthService:
    async def create_user(self, db: Session, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse.model_validate(new_user)
    
    async def authenticate_user(self, db: Session, username: str, password: str) -> Token:
        """Authenticate user and return JWT token"""
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        user_response = UserResponse.model_validate(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    async def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> UserResponse:
        """Update user profile"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Check email uniqueness if email is being updated
        if "email" in update_data:
            existing_user = db.query(User).filter(
                User.email == update_data["email"],
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("Email already taken")
        
        # Update user
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def delete_user(self, db: Session, user_id: int):
        """Delete user account (soft delete)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Soft delete by deactivating
        user.is_active = False
        db.commit()

