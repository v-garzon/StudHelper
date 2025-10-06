from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse, Token
from app.utils.security import get_password_hash, verify_password, create_access_token, validate_password_strength
from app.firebase_admin import verify_firebase_token
from datetime import timedelta
from app.config import get_settings
from typing import Optional
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class AuthService:
    
    def _get_display_name(self, user: User) -> str:
        """Get display name: alias if set, otherwise 'Name Surname'"""
        if user.alias:
            return user.alias
        return f"{user.name} {user.surname}"
    
    async def create_user(self, db: Session, user_data: UserCreate) -> UserResponse:
        """Create a new user with email/password (legacy method)"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Validate password strength
        password_validation = validate_password_strength(user_data.password)
        if not password_validation['valid']:
            raise ValueError(f"Password does not meet requirements: {', '.join(password_validation['errors'])}")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            surname=user_data.surname,
            alias=user_data.alias,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        user_response = UserResponse.model_validate(new_user)
        user_response.display_name = self._get_display_name(new_user)
        return user_response
    
    async def authenticate_user(self, db: Session, email: str, password: str) -> Token:
        """Authenticate user with email/password (legacy method)"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise ValueError(f"No account found with email {email}")
        if not user.is_active:
            raise ValueError("Account is deactivated")
        if not user.hashed_password:
            raise ValueError("This account uses social login. Please sign in with Google or Microsoft.")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Incorrect password")
        
        # Create JWT token with user.id as subject
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        user_response = UserResponse.model_validate(user)
        user_response.display_name = self._get_display_name(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    async def firebase_authenticate(self, db: Session, id_token: str, 
                                    name: Optional[str] = None,
                                    surname: Optional[str] = None,
                                    alias: Optional[str] = None) -> Token:
        """
        Authenticate user via Firebase token
        Creates user if first time, returns JWT token
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
                # Use provided name/surname or parse from display_name
                if not name or not surname:
                    # Try to split display_name from OAuth
                    name_parts = display_name.split(' ', 1) if display_name else ['User', 'Name']
                    name = name or name_parts[0]
                    surname = surname or (name_parts[1] if len(name_parts) > 1 else 'Unknown')
                
                user = User(
                    email=email,
                    name=name,
                    surname=surname,
                    alias=alias,
                    firebase_uid=firebase_uid,
                    auth_provider=auth_provider,
                    email_verified=email_verified,
                    hashed_password=None,
                    is_active=True
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                logger.info(f"New Firebase user created: {email} via {auth_provider}")
        
        # Step 3: Create JWT token with user.id as subject
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        user_response = UserResponse.model_validate(user)
        user_response.display_name = self._get_display_name(user)
        
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
        
        user_response = UserResponse.model_validate(user)
        user_response.display_name = self._get_display_name(user)
        return user_response
    
    async def delete_user(self, db: Session, user_id: int):
        """Delete user account (soft delete)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Soft delete by deactivating
        user.is_active = False
        db.commit()


