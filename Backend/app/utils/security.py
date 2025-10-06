from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.config import get_settings
from app.schemas import UserResponse
import logging
import re

settings = get_settings()
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> dict:
    """
    Validate password meets requirements:
    - At least 6 characters
    - At least 1 uppercase letter
    - At least 1 number
    
    Returns dict with 'valid' (bool) and 'errors' (list)
    """
    errors = []
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least 1 uppercase letter")
    
    number_count = len(re.findall(r'\d', password))
    if number_count < 1:
        errors.append(f"Password must contain at least 1 number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def _get_display_name(user) -> str:
    """Helper function to get display name"""
    if user.alias:
        return user.alias
    return f"{user.name} {user.surname}"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        # Convert to integer
        user_id = int(user_id_str)
            
    except (JWTError, ValueError):
        raise credentials_exception
    
    # Get user from database by ID
    from app.models import User
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    user_response = UserResponse.model_validate(user)
    user_response.display_name = _get_display_name(user)
    return user_response


