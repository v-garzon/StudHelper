"""Test configuration and fixtures."""

import httpx
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import respx

from src.main import app
from src.core.database import Base, get_db_session
from src.auth.service import AuthService
from src.auth.models import User
from src.config import get_settings
from src.auth.schemas import UserCreate

# Test settings
settings = get_settings()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for fast tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()
    if os.path.exists("./test.db"):
        os.unlink("./test.db")


@pytest.fixture
async def db_session(test_engine):
    """Create database session for tests."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Create test client with database override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    auth_service = AuthService(db_session)
    user = await auth_service.create_user(UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
    ))
    return user


@pytest.fixture
async def auth_headers(test_user):
    """Create authentication headers."""
    from src.auth.jwt_handler import create_access_token

    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    with respx.mock:
        # Mock chat completions
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json={
                "choices": [{
                    "message": {"content": "Mock AI response"},
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 20,
                    "total_tokens": 70
                },
                "model": "gpt-4o-mini"
            })
        )
        
        # Mock embeddings
        respx.post("https://api.openai.com/v1/embeddings").mock(
            return_value=httpx.Response(200, json={
                "data": [{"embedding": [0.1] * 1536}],
                "usage": {"total_tokens": 10}
            })
        )
        
        yield


@pytest.fixture
def sample_pdf_content() -> bytes:
    """Create sample PDF content."""
    return b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\nxref\n0 3\n0000000000 65535 f \ntrailer\n<</Size 3/Root 1 0 R>>\nstartxref\n9\n%%EOF"


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir