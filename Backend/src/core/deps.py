"""FastAPI dependency functions."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_handler import decode_jwt_token
from src.auth.models import User
from src.auth.service import AuthService
from src.core.database import get_db_session
from src.auth.schemas import UserCreate

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get current authenticated user."""
    try:
        payload = decode_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_default_user(
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Get or create default user for single-user mode."""
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email("default@studhelper.local")
    
    if not user:
        # Create default user
        user = await auth_service.create_user(UserCreate(
            email="default@studhelper.com",
            username="default_user",
            password="default_password_change_me",
        ))
    
    return user


