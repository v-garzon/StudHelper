import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "newpassword"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    print(f"Response: {response.status_code}, {response.text}")  
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    user_data = {
        "email": test_user.email,
        "username": "newuser",
        "password": "password"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username"""
    user_data = {
        "email": "newemail@example.com",
        "username": test_user.username,
        "password": "password"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test successful login"""
    login_data = {"username": test_user.username, "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == test_user.username

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {"username": "wronguser", "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_get_current_user(client, auth_headers_student, test_user):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers_student)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email

def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

def test_update_profile(client, auth_headers_student, test_user):
    """Test updating user profile"""
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }
    response = client.put("/api/v1/auth/profile", json=update_data, headers=auth_headers_student)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["email"] == update_data["email"]

def test_delete_account(client, auth_headers_student):
    """Test deleting user account"""
    response = client.delete("/api/v1/auth/account", headers=auth_headers_student)
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]

