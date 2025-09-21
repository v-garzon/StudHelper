"""Authentication tests."""

import pytest
from httpx import AsyncClient

from src.auth.service import AuthService
from src.auth.schemas import UserCreate
from src.core.exceptions import ValidationError, AuthenticationError


class TestAuthService:
    """Test authentication service."""
    
    async def test_create_user(self, db_session):
        """Test user creation."""
        auth_service = AuthService(db_session)
        
        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            password="password123",
        )
        
        user = await auth_service.create_user(user_data)
        
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.hashed_password != "password123"  # Should be hashed
        assert user.is_active is True
    
    async def test_create_duplicate_user(self, db_session, test_user):
        """Test creating user with duplicate email."""
        auth_service = AuthService(db_session)
        
        user_data = UserCreate(
            email=test_user.email,
            username="different",
            password="password123",
        )
        
        with pytest.raises(ValidationError, match="already exists"):
            await auth_service.create_user(user_data)
    
    async def test_authenticate_user(self, db_session, test_user):
        """Test user authentication."""
        auth_service = AuthService(db_session)
        
        # Valid credentials
        user = await auth_service.authenticate_user(test_user.email, "testpass123")
        assert user is not None
        assert user.id == test_user.id
        
        # Invalid password
        user = await auth_service.authenticate_user(test_user.email, "wrongpass")
        assert user is None
        
        # Invalid email
        user = await auth_service.authenticate_user("wrong@example.com", "testpass123")
        assert user is None


class TestAuthRoutes:
    """Test authentication routes."""
    
    async def test_register_user(self, client: AsyncClient):
        """Test user registration endpoint."""
        response = await client.post("/api/v1/auth/register", json={
            "email": "register@example.com",
            "username": "registeruser",
            "password": "password123",
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "register@example.com"
        assert data["username"] == "registeruser"
        assert "id" in data
    
    async def test_login_user(self, client: AsyncClient, test_user):
        """Test user login endpoint."""
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user.email,
            "password": "testpass123",
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpass",
        })
        
        assert response.status_code == 401
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user info."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

