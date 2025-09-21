"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginRequest, LoginResponse, UserCreate, UserResponse
from src.auth.service import AuthService
from src.core.database import get_db_session
from src.core.deps import get_current_user  # Add this line
from src.core.exceptions import AuthenticationError, ValidationError

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user."""
    try:
        auth_service = AuthService(db)
        user = await auth_service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Login user."""
    try:
        auth_service = AuthService(db)
        return await auth_service.login(login_data.email, login_data.password)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """Get current user information."""
    return UserResponse.model_validate(current_user)


