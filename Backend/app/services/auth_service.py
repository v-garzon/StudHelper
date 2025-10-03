from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.firebase_admin import verify_firebase_token
from datetime import timedelta
from app.config import get_settings
from typing import Optional
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class AuthService:
    async def create_user(self, db: Session, user_data: UserCreate) -> UserResponse:
        """Create a new user with email/password (legacy method, kept for compatibility)"""
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
        """Authenticate user with email/password (legacy method)"""
        # Check if username is an email or actual username
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            raise ValueError(f"Username or email {username} does not exist")
        if not user.is_active:
            raise ValueError("Account is deactivated")
        if not user.hashed_password:
            raise ValueError("This account uses social login. Please sign in with Google or Microsoft.")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Incorrect password")
        
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
    
    async def firebase_authenticate(self, db: Session, id_token: str, 
                                    username: Optional[str] = None,
                                    full_name: Optional[str] = None) -> Token:
        """
        Authenticate user via Firebase token
        Creates user if first time, returns JWT token
        
        Args:
            db: Database session
            id_token: Firebase ID token from frontend
            username: Optional username for email/password registration
            full_name: Optional full name for email/password registration
        
        Returns:
            Token with JWT and user data
        """
        # Step 1: Verify Firebase token
        try:
            decoded_token = verify_firebase_token(id_token)
        except ValueError as e:
            raise ValueError(f"Firebase authentication failed: {str(e)}")
        
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        email_verified = decoded_token.get('email_verified', False)
        display_name = decoded_token.get('name', '')
        
        # Determine provider
        provider_data = decoded_token.get('firebase', {}).get('sign_in_provider', 'unknown')
        if provider_data == 'google.com':
            auth_provider = 'google'
        elif provider_data == 'microsoft.com':
            auth_provider = 'microsoft'
        elif provider_data == 'password':
            auth_provider = 'firebase_email'
        else:
            auth_provider = 'firebase'
        
        if not email:
            raise ValueError("Email not provided by Firebase")
        
        # Step 2: Check if user exists by firebase_uid
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if user:
            # Existing Firebase user - update verification status
            user.email_verified = email_verified
            db.commit()
            db.refresh(user)
            logger.info(f"Existing Firebase user logged in: {email}")
        else:
            # Check if email already exists (user switching from email/password to OAuth)
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Link existing account to Firebase
                logger.info(f"Linking existing account to Firebase: {email}")
                user.firebase_uid = firebase_uid
                user.auth_provider = auth_provider
                user.email_verified = email_verified
                db.commit()
                db.refresh(user)
            else:
                # New user - create account
                # Use provided username or generate from email
                if not username:
                    username = self._generate_username_from_email(email, db)
                
                # Use provided full_name or display name from OAuth
                if not full_name:
                    full_name = display_name
                
                user = User(
                    email=email,
                    username=username,
                    full_name=full_name,
                    firebase_uid=firebase_uid,
                    auth_provider=auth_provider,
                    email_verified=email_verified,
                    hashed_password=None,  # No password for Firebase users
                    is_active=True
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                logger.info(f"New Firebase user created: {email} via {auth_provider}")
        
        # Step 3: Create YOUR JWT token
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
    
    def _generate_username_from_email(self, email: str, db: Session) -> str:
        """Generate unique username from email"""
        base_username = email.split('@')[0].lower()
        # Remove special characters
        base_username = ''.join(c for c in base_username if c.isalnum() or c == '_')
        username = base_username
        counter = 1
        
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
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


