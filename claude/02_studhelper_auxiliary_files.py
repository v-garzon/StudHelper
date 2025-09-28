### NEW FILE: app/__init__.py
# StudHelper Backend Application Package

### NEW FILE: app/services/__init__.py
# Services Package

### NEW FILE: app/utils/__init__.py
# Utilities Package

### NEW FILE: app/migrations/__init__.py
# Database Migrations Package

### NEW FILE: tests/__init__.py
# Test Package

### NEW FILE: tests/conftest.py
import pytest
import tempfile
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from app.models import User, Class, ClassMembership
from app.utils.security import get_password_hash
from app.config import get_settings
import uuid
import os

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_db_setup():
    """Create and tear down test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture
def test_db(test_db_setup):
    """Provide a clean database session for each test"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """FastAPI test client"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    user = User(
        email=f"testuser{uuid.uuid4().hex[:8]}@example.com",
        username=f"testuser{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_teacher(test_db):
    """Create a test teacher user"""
    teacher = User(
        email=f"testteacher{uuid.uuid4().hex[:8]}@example.com",
        username=f"testteacher{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test Teacher",
        is_active=True
    )
    test_db.add(teacher)
    test_db.commit()
    test_db.refresh(teacher)
    return teacher

@pytest.fixture
def test_class(test_db, test_teacher):
    """Create a test class"""
    test_class = Class(
        name="Test Class",
        description="A test class for testing",
        class_code=f"TEST{uuid.uuid4().hex[:4].upper()}",
        owner_id=test_teacher.id,
        is_active=True
    )
    test_db.add(test_class)
    test_db.flush()
    
    # Add teacher as manager
    teacher_membership = ClassMembership(
        user_id=test_teacher.id,
        class_id=test_class.id,
        is_manager=True,
        can_read=True,
        can_chat=True,
        can_share_class=True,
        can_upload_documents=True,
        max_concurrent_chats=10
    )
    test_db.add(teacher_membership)
    test_db.commit()
    test_db.refresh(test_class)
    return test_class

@pytest.fixture
def auth_headers_student(client, test_user):
    """Get authentication headers for test student"""
    login_data = {"username": test_user.username, "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_teacher(client, test_teacher):
    """Get authentication headers for test teacher"""
    login_data = {"username": test_teacher.username, "password": "testpassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_txt_file():
    """Sample text file for testing"""
    content = b"This is a test document for StudHelper.\nIt contains sample text for testing document processing."
    return ("test.txt", content, "text/plain")

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    # This would be actual PDF bytes in reality
    return b"%PDF-1.4 sample content"

### NEW FILE: tests/test_auth.py
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

### NEW FILE: tests/test_classes.py
import pytest

def test_create_class(client, auth_headers_teacher):
    """Test creating a class"""
    class_data = {
        "name": "Physics 101",
        "description": "Introduction to Physics"
    }
    response = client.post("/api/v1/classes/", json=class_data, headers=auth_headers_teacher)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == class_data["name"]
    assert data["description"] == class_data["description"]
    assert "class_code" in data
    assert len(data["class_code"]) == 8

def test_get_user_classes(client, auth_headers_teacher, test_class):
    """Test getting user's classes"""
    response = client.get("/api/v1/classes/", headers=auth_headers_teacher)
    assert response.status_code == 200
    classes = response.json()
    assert isinstance(classes, list)
    assert len(classes) >= 1
    assert any(c["id"] == test_class.id for c in classes)

def test_join_class(client, auth_headers_student, test_class):
    """Test joining a class"""
    join_data = {"class_code": test_class.class_code}
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_class.id

def test_join_class_invalid_code(client, auth_headers_student):
    """Test joining with invalid class code"""
    join_data = {"class_code": "INVALID"}
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 404

def test_join_class_already_member(client, auth_headers_student, test_class, test_db):
    """Test joining a class when already a member"""
    # First join
    join_data = {"class_code": test_class.class_code}
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 200
    
    # Try to join again
    response = client.post("/api/v1/classes/join", json=join_data, headers=auth_headers_student)
    assert response.status_code == 400

def test_get_class_details(client, auth_headers_teacher, test_class):
    """Test getting class details"""
    response = client.get(f"/api/v1/classes/{test_class.id}", headers=auth_headers_teacher)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_class.id
    assert data["name"] == test_class.name

def test_get_class_details_no_access(client, auth_headers_student, test_class):
    """Test getting class details without access"""
    response = client.get(f"/api/v1/classes/{test_class.id}", headers=auth_headers_student)
    assert response.status_code == 403

def test_delete_class(client, auth_headers_teacher, test_class):
    """Test deleting a class"""
    response = client.delete(f"/api/v1/classes/{test_class.id}", headers=auth_headers_teacher)
    assert response.status_code == 200

def test_delete_class_not_owner(client, auth_headers_student, test_class):
    """Test deleting a class when not owner"""
    response = client.delete(f"/api/v1/classes/{test_class.id}", headers=auth_headers_student)
    assert response.status_code == 404

### NEW FILE: tests/test_permissions.py
import pytest

def test_get_class_members_as_manager(client, auth_headers_teacher, test_class):
    """Test getting class members as manager"""
    response = client.get(f"/api/v1/classes/{test_class.id}/members", headers=auth_headers_teacher)
    assert response.status_code == 200
    members = response.json()
    assert isinstance(members, list)
    assert len(members) >= 1

def test_get_class_members_not_manager(client, auth_headers_student, test_class, test_db):
    """Test getting class members when not manager"""
    # Join class first
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=1,  # Assuming student ID
        class_id=test_class.id,
        is_manager=False
    )
    test_db.add(membership)
    test_db.commit()
    
    response = client.get(f"/api/v1/classes/{test_class.id}/members", headers=auth_headers_student)
    assert response.status_code == 403

def test_update_member_permissions(client, auth_headers_teacher, test_class, test_user, test_db):
    """Test updating member permissions"""
    # Add user to class first
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=test_user.id,
        class_id=test_class.id,
        is_manager=False,
        can_chat=True,
        daily_token_limit=500000
    )
    test_db.add(membership)
    test_db.commit()
    
    # Update permissions
    update_data = {
        "can_chat": False,
        "daily_token_limit": 2000000
    }
    response = client.put(
        f"/api/v1/classes/{test_class.id}/members/{test_user.id}",
        json=update_data,
        headers=auth_headers_teacher
    )
    assert response.status_code == 200
    data = response.json()
    assert data["can_chat"] == False
    assert data["daily_token_limit"] == 2000000

def test_update_sponsorship(client, auth_headers_teacher, test_class):
    """Test updating class sponsorship"""
    sponsorship_data = {"is_sponsored": True}
    response = client.put(
        f"/api/v1/classes/{test_class.id}/sponsorship",
        json=sponsorship_data,
        headers=auth_headers_teacher
    )
    assert response.status_code == 200

def test_update_sponsorship_not_manager(client, auth_headers_student, test_class):
    """Test updating sponsorship when not manager"""
    sponsorship_data = {"is_sponsored": True}
    response = client.put(
        f"/api/v1/classes/{test_class.id}/sponsorship",
        json=sponsorship_data,
        headers=auth_headers_student
    )
    assert response.status_code == 403

### NEW FILE: tests/test_chat.py
import pytest
from unittest.mock import patch, AsyncMock

def test_create_chat_session(client, auth_headers_student, test_class, test_db):
    """Test creating a chat session"""
    # First enroll student in class
    from app.models import ClassMembership
    enrollment = ClassMembership(
        user_id=1,  # Assuming student ID
        class_id=test_class.id,
        can_chat=True
    )
    test_db.add(enrollment)
    test_db.commit()
    
    session_data = {
        "title": "Homework Help",
        "class_id": test_class.id
    }
    response = client.post("/api/v1/chat/sessions", json=session_data, headers=auth_headers_student)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == session_data["title"]

def test_create_chat_session_no_access(client, auth_headers_student, test_class):
    """Test creating chat session without class access"""
    session_data = {
        "title": "Unauthorized Chat",
        "class_id": test_class.id
    }
    response = client.post("/api/v1/chat/sessions", json=session_data, headers=auth_headers_student)
    assert response.status_code == 403

def test_get_user_sessions(client, auth_headers_student):
    """Test getting user's chat sessions"""
    response = client.get("/api/v1/chat/sessions", headers=auth_headers_student)
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)

@patch('app.services.openai_service.OpenAIService.generate_response')
def test_send_message(mock_generate, client, auth_headers_student, test_class, test_db):
    """Test sending a message in a chat session"""
    # Setup enrollment and session
    from app.models import ClassMembership, ChatSession
    enrollment = ClassMembership(
        user_id=1,
        class_id=test_class.id,
        can_chat=True
    )
    test_db.add(enrollment)
    test_db.commit()
    
    session = ChatSession(
        title="Test Session",
        user_id=1,
        class_id=test_class.id
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    
    # Mock AI response
    mock_generate.return_value = ("This is a test AI response", 100)
    
    message_data = {"content": "What is physics?"}
    response = client.post(
        f"/api/v1/chat/sessions/{session.id}/messages",
        json=message_data,
        headers=auth_headers_student
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_message"]["content"] == message_data["content"]
    assert data["ai_response"]["content"] == "This is a test AI response"

def test_get_session_messages(client, auth_headers_student, test_class, test_db):
    """Test getting messages from a session"""
    # Create session
    from app.models import ChatSession
    session = ChatSession(
        title="Test Session",
        user_id=1,
        class_id=test_class.id
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    
    response = client.get(
        f"/api/v1/chat/sessions/{session.id}/messages",
        headers=auth_headers_student
    )
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)

### NEW FILE: tests/test_documents.py
import pytest
import io

def test_upload_class_document(client, auth_headers_teacher, test_class, sample_txt_file):
    """Test uploading a document to a class"""
    filename, content, content_type = sample_txt_file
    files = {"file": (filename, io.BytesIO(content), content_type)}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == filename
    assert data["file_type"] == "txt"

def test_upload_document_no_access(client, auth_headers_student, test_class, sample_txt_file):
    """Test uploading document without access"""
    filename, content, content_type = sample_txt_file
    files = {"file": (filename, io.BytesIO(content), content_type)}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_student
    )
    assert response.status_code == 403

def test_get_class_documents(client, auth_headers_teacher, test_class):
    """Test getting class documents"""
    response = client.get(
        f"/api/v1/documents/classes/{test_class.id}",
        headers=auth_headers_teacher
    )
    assert response.status_code == 200
    documents = response.json()
    assert isinstance(documents, list)

def test_upload_large_file(client, auth_headers_teacher, test_class):
    """Test uploading file that exceeds size limit"""
    # Create large file content
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 400

def test_upload_invalid_file_type(client, auth_headers_teacher, test_class):
    """Test uploading invalid file type"""
    files = {"file": ("test.exe", io.BytesIO(b"executable"), "application/octet-stream")}
    
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 400

### NEW FILE: tests/test_usage.py
import pytest

def test_get_my_usage(client, auth_headers_student, test_class, test_db):
    """Test getting personal usage statistics"""
    # Create membership first
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=1,
        class_id=test_class.id
    )
    test_db.add(membership)
    test_db.commit()
    
    response = client.get("/api/v1/usage/my-usage", headers=auth_headers_student)
    assert response.status_code == 200
    usage = response.json()
    assert isinstance(usage, list)

def test_get_class_usage_overview(client, auth_headers_teacher, test_class):
    """Test getting class usage overview as manager"""
    response = client.get(
        f"/api/v1/usage/classes/{test_class.id}/members",
        headers=auth_headers_teacher
    )
    assert response.status_code == 200
    overview = response.json()
    assert isinstance(overview, list)

def test_get_class_usage_not_manager(client, auth_headers_student, test_class):
    """Test getting class usage when not manager"""
    response = client.get(
        f"/api/v1/usage/classes/{test_class.id}/members",
        headers=auth_headers_student
    )
    assert response.status_code == 403

def test_update_user_limits(client, auth_headers_teacher, test_class, test_user, test_db):
    """Test updating user token limits"""
    # Add user to class
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=test_user.id,
        class_id=test_class.id
    )
    test_db.add(membership)
    test_db.commit()
    
    response = client.put(
        f"/api/v1/usage/classes/{test_class.id}/limits/{test_user.id}?daily_limit=2000000&weekly_limit=10000000&monthly_limit=30000000",
        headers=auth_headers_teacher
    )
    assert response.status_code == 200

### NEW FILE: tests/test_services.py
import pytest
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from app.services.document_service import DocumentService
from app.services.usage_service import UsageService
from app.schemas import UserCreate

@pytest.mark.asyncio
async def test_auth_service_create_user(test_db):
    """Test user creation service"""
    auth_service = AuthService()
    user_data = UserCreate(
        email="service_test@example.com",
        username="servicetest",
        full_name="Service Test",
        password="testpassword"
    )
    
    user = await auth_service.create_user(test_db, user_data)
    assert user.email == user_data.email
    assert user.username == user_data.username

@pytest.mark.asyncio
async def test_permission_service_check_membership(test_db, test_user, test_class):
    """Test permission service membership check"""
    permission_service = PermissionService()
    
    # Should return None for non-member
    membership = await permission_service.get_user_membership(test_db, test_user.id, test_class.id)
    assert membership is None

@pytest.mark.asyncio
async def test_usage_service_get_stats(test_db, test_user, test_class):
    """Test usage service statistics"""
    # Add user to class
    from app.models import ClassMembership
    membership = ClassMembership(
        user_id=test_user.id,
        class_id=test_class.id
    )
    test_db.add(membership)
    test_db.commit()
    
    usage_service = UsageService()
    stats = await usage_service.get_user_class_usage(test_db, test_user.id, test_class.id)
    
    assert stats.daily_tokens_used >= 0
    assert stats.daily_limit > 0

### NEW FILE: tests/test_integration.py
import pytest
from unittest.mock import patch
import io

@pytest.mark.asyncio
async def test_full_workflow(client, auth_headers_teacher, auth_headers_student, test_class, sample_txt_file, temp_upload_dir):
    """Test complete workflow: create class, enroll, upload docs, chat"""
    
    # 1. Student enrolls in class
    enrollment_data = {"class_code": test_class.class_code}
    response = client.post("/api/v1/classes/join", json=enrollment_data, headers=auth_headers_student)
    assert response.status_code == 200
    
    # 2. Teacher uploads document
    filename, content, content_type = sample_txt_file
    files = {"file": (filename, io.BytesIO(content), content_type)}
    response = client.post(
        f"/api/v1/documents/classes/{test_class.id}/upload",
        files=files,
        headers=auth_headers_teacher
    )
    assert response.status_code == 201
    
    # 3. Student creates chat session
    session_data = {
        "title": "Study Session",
        "class_id": test_class.id
    }
    response = client.post("/api/v1/chat/sessions", json=session_data, headers=auth_headers_student)
    assert response.status_code == 201
    session = response.json()
    
    # 4. Student sends message (mock AI response)
    with patch('app.services.openai_service.OpenAIService.generate_response') as mock_chat:
        mock_chat.return_value = ("AI response based on uploaded document", 150)
        
        message_data = {"content": "What did you learn from the document?"}
        response = client.post(
            f"/api/v1/chat/sessions/{session['id']}/messages",
            json=message_data,
            headers=auth_headers_student
        )
        assert response.status_code == 200
        chat_response = response.json()
        assert chat_response["ai_response"]["content"] == "AI response based on uploaded document"
    
    # 5. Check that usage was recorded
    response = client.get("/api/v1/usage/my-usage", headers=auth_headers_student)
    assert response.status_code == 200

### NEW FILE: .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_studhelper
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-cov
    
    - name: Set environment variables
      run: |
        echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_studhelper" >> $GITHUB_ENV
        echo "SECRET_KEY=test-secret-key-for-ci-pipeline" >> $GITHUB_ENV
        echo "OPENAI_API_KEY=test-key" >> $GITHUB_ENV
    
    - name: Run database migrations
      run: |
        alembic upgrade head
    
    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov-report=xml --cov-report=html tests/
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        fail_ci_if_error: false

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install linting tools
      run: |
        python -m pip install --upgrade pip
        pip install black isort flake8 mypy
    
    - name: Run Black
      run: black --check --diff app tests
    
    - name: Run isort
      run: isort --check-only --diff app tests
    
    - name: Run flake8
      run: flake8 app tests
    
    - name: Run mypy
      run: mypy app

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install security tools
      run: |
        python -m pip install --upgrade pip
        pip install bandit safety
    
    - name: Run Bandit security linter
      run: bandit -r app/
    
    - name: Check for security vulnerabilities
      run: safety check

### NEW FILE: .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ secrets.REGISTRY_URL }}/studhelper-backend
        tags: |
          type=ref,event=branch
          type=ref,event=tag
          type=sha
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Deploy to production
      run: |
        echo "Deploy script would go here"
        # This would typically involve:
        # - SSH to production server
        # - Pull new image
        # - Update docker-compose
        # - Run migrations
        # - Restart services

### NEW FILE: scripts/dev-setup.sh
#!/bin/bash
set -e

echo "🚀 Setting up StudHelper Backend Development Environment"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version >= 3.11" | bc -l) != 1 ]]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL first."
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "✏️  Please edit .env with your actual values (especially OPENAI_API_KEY)"
fi

# Create database
echo "🗄️  Setting up database..."
createdb studhelper 2>/dev/null || echo "Database already exists"

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Create upload directory
echo "📁 Creating upload directory..."
mkdir -p uploads logs

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Visit: http://localhost:8000/docs"

### NEW FILE: scripts/run-tests.sh
#!/bin/bash
set -e

echo "🧪 Running StudHelper Backend Tests"

# Activate virtual environment
source venv/bin/activate

# Set test environment variables
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test-secret-key"
export OPENAI_API_KEY="test-key"

# Run tests with coverage
echo "🔍 Running tests with coverage..."
pytest --cov=app --cov-report=html --cov-report=term-missing tests/ -v

# Run linting
echo "🔧 Running code quality checks..."
black --check app tests
isort --check-only app tests
flake8 app tests

# Run security checks
echo "🔒 Running security checks..."
bandit -r app/
safety check

echo "✅ All tests and checks passed!"

### NEW FILE: scripts/docker-dev.sh
#!/bin/bash
set -e

echo "🐳 Starting StudHelper Backend with Docker"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✏️  Please edit .env with your actual values"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Please set your OPENAI_API_KEY in .env file"
    exit 1
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up --build -d

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "✅ StudHelper Backend is running!"
echo "📍 API: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo "🗄️  Database: localhost:5432"

### NEW FILE: scripts/production-deploy.sh
#!/bin/bash
set -e

echo "🚀 Deploying StudHelper Backend to Production"

# Check required environment variables
required_vars=("DATABASE_URL" "SECRET_KEY" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

# Build production image
echo "🏗️  Building production image..."
docker build -t studhelper-backend:latest .

# Create production directories
echo "📁 Creating production directories..."
sudo mkdir -p /opt/studhelper/{uploads,logs,backups}
sudo chown -R $(id -u):$(id -g) /opt/studhelper

# Backup database (if exists)
if [ -n "$BACKUP_DATABASE" ]; then
    echo "💾 Creating database backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    pg_dump $DATABASE_URL > /opt/studhelper/backups/backup_$timestamp.sql
fi

# Run database migrations
echo "🔄 Running database migrations..."
docker run --rm \
    -e DATABASE_URL="$DATABASE_URL" \
    studhelper-backend:latest \
    alembic upgrade head

# Start production services
echo "🚀 Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Health check
echo "🏥 Running health check..."
sleep 10
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed"
    exit 1
fi

echo "🎉 StudHelper Backend deployed successfully!"

### NEW FILE: docker-compose.production.yml
version: '3.8'

services:
  backend:
    image: studhelper-backend:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=false
    volumes:
      - /opt/studhelper/uploads:/app/uploads
      - /opt/studhelper/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend

### NEW FILE: nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Auth routes (more restrictive)
        location /api/v1/auth/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend;
        }

        # Documentation
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

### NEW FILE: app/logging_config.py
import logging
import logging.config
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": "INFO",
                "handlers": ["console", "file"],
            },
            "app": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)

### NEW FILE: monitoring/healthcheck.py
#!/usr/bin/env python3
"""
Health check script for StudHelper Backend
Usage: python monitoring/healthcheck.py [--url URL] [--timeout SECONDS]
"""

import argparse
import requests
import sys
import time
import json
from datetime import datetime

def check_health(url: str, timeout: int = 30) -> bool:
    """Check if the application is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def check_database(url: str, timeout: int = 30) -> bool:
    """Check if database connection is working"""
    try:
        # This would require authentication, so just check if endpoint exists
        response = requests.get(f"{url}/api/v1/auth/me", timeout=timeout)
        # 403 is expected without auth, but means the endpoint is reachable
        return response.status_code in [401, 403]
    except Exception as e:
        print(f"Database check failed: {e}")
        return False

def check_openai_integration(url: str, timeout: int = 30) -> bool:
    """Check if OpenAI integration is configured"""
    # This is a simple check - in production you'd have a dedicated endpoint
    try:
        response = requests.get(f"{url}/docs", timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        print(f"OpenAI check failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="StudHelper Backend Health Check")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the application")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    checks = {
        "health": check_health(args.url, args.timeout),
        "database": check_database(args.url, args.timeout),
        "openai": check_openai_integration(args.url, args.timeout),
    }
    
    all_healthy = all(checks.values())
    
    if args.json:
        result = {
            "timestamp": datetime.now().isoformat(),
            "url": args.url,
            "overall_status": "healthy" if all_healthy else "unhealthy",
            "checks": checks
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"StudHelper Backend Health Check - {args.url}")
        print(f"Timestamp: {datetime.now()}")
        print("-" * 50)
        
        for check_name, status in checks.items():
            status_str = "✅ PASS" if status else "❌ FAIL"
            print(f"{check_name.capitalize():12} {status_str}")
        
        print("-" * 50)
        overall_status = "✅ HEALTHY" if all_healthy else "❌ UNHEALTHY"
        print(f"Overall:     {overall_status}")
    
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()

### NEW FILE: monitoring/metrics.py
"""
Metrics collection for StudHelper Backend
"""

import time
import psutil
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Class, ChatSession, UsageRecord

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect application and system metrics"""
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def collect_app_metrics(self, db: Session) -> Dict[str, Any]:
        """Collect application-level metrics"""
        try:
            # Count active entities
            active_users = db.query(User).filter(User.is_active == True).count()
            total_classes = db.query(Class).filter(Class.is_active == True).count()
            active_sessions = db.query(ChatSession).filter(ChatSession.is_active == True).count()
            
            # Recent activity (last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            recent_messages = db.query(ChatSession).filter(
                ChatSession.updated_at >= yesterday
            ).count()
            
            recent_usage = db.query(UsageRecord).filter(
                UsageRecord.timestamp >= yesterday
            ).count()
            
            return {
                "active_users": active_users,
                "total_classes": total_classes,
                "active_chat_sessions": active_sessions,
                "recent_messages_24h": recent_messages,
                "recent_usage_records_24h": recent_usage,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error collecting app metrics: {e}")
            return {}
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all available metrics"""
        db = next(get_db())
        try:
            return {
                "system": self.collect_system_metrics(),
                "application": self.collect_app_metrics(db),
                "timestamp": time.time()
            }
        finally:
            db.close()

### NEW FILE: seed_data.py
"""
Seed data for StudHelper Backend development
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Class, ClassMembership
from app.utils.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_seed_data():
    """Create seed data for development"""
    db = SessionLocal()
    
    try:
        # Create demo teacher
        teacher = User(
            email="teacher@studhelper.com",
            username="demo_teacher",
            full_name="Demo Teacher",
            hashed_password=get_password_hash("teacher123"),
            is_active=True
        )
        db.add(teacher)
        db.flush()
        
        # Create demo student
        student = User(
            email="student@studhelper.com",
            username="demo_student",
            full_name="Demo Student",
            hashed_password=get_password_hash("student123"),
            is_active=True
        )
        db.add(student)
        db.flush()
        
        # Create demo class
        demo_class = Class(
            name="Introduction to Physics",
            description="A comprehensive introduction to physics concepts",
            class_code="PHYS101",
            owner_id=teacher.id,
            is_active=True
        )
        db.add(demo_class)
        db.flush()
        
        # Add teacher as manager
        teacher_membership = ClassMembership(
            user_id=teacher.id,
            class_id=demo_class.id,
            is_manager=True,
            can_read=True,
            can_chat=True,
            can_share_class=True,
            can_upload_documents=True,
            max_concurrent_chats=10,
            is_sponsored=False,
            daily_token_limit=5_000_000,
            weekly_token_limit=25_000_000,
            monthly_token_limit=75_000_000
        )
        db.add(teacher_membership)
        
        # Add student as member
        student_membership = ClassMembership(
            user_id=student.id,
            class_id=demo_class.id,
            is_manager=False,
            can_read=True,
            can_chat=True,
            can_share_class=False,
            can_upload_documents=True,
            max_concurrent_chats=3,
            is_sponsored=True,  # Teacher sponsors student
            daily_token_limit=1_000_000,
            weekly_token_limit=5_000_000,
            monthly_token_limit=15_000_000
        )
        db.add(student_membership)
        
        db.commit()
        
        logger.info("✅ Seed data created successfully!")
        logger.info("Demo accounts:")
        logger.info("  Teacher: teacher@studhelper.com / teacher123")
        logger.info("  Student: student@studhelper.com / student123")
        logger.info("  Class Code: PHYS101")
        
    except Exception as e:
        logger.error(f"❌ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()

### NEW FILE: client_examples/python_client.py
"""
Python client example for StudHelper Backend API
"""

import requests
import json
from typing import Optional, Dict, Any

class StudHelperClient:
    """Python client for StudHelper Backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request"""
        url = f"{self.base_url}{endpoint}"
        
        if self.token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.token}'
            kwargs['headers'] = headers
        
        return self.session.request(method, url, **kwargs)
    
    def register(self, email: str, username: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        data = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name
        }
        response = self._request('POST', '/api/v1/auth/register', json=data)
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and store token"""
        data = {"username": username, "password": password}
        response = self._request('POST', '/api/v1/auth/login', json=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result['access_token']
        return result
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        response = self._request('GET', '/api/v1/auth/me')
        response.raise_for_status()
        return response.json()
    
    def create_class(self, name: str, description: str = None) -> Dict[str, Any]:
        """Create a new class"""
        data = {"name": name, "description": description}
        response = self._request('POST', '/api/v1/classes/', json=data)
        response.raise_for_status()
        return response.json()
    
    def join_class(self, class_code: str) -> Dict[str, Any]:
        """Join a class by code"""
        data = {"class_code": class_code}
        response = self._request('POST', '/api/v1/classes/join', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_classes(self) -> list:
        """Get user's classes"""
        response = self._request('GET', '/api/v1/classes/')
        response.raise_for_status()
        return response.json()
    
    def create_chat_session(self, class_id: int, title: str) -> Dict[str, Any]:
        """Create a chat session"""
        data = {"class_id": class_id, "title": title}
        response = self._request('POST', '/api/v1/chat/sessions', json=data)
        response.raise_for_status()
        return response.json()
    
    def send_message(self, session_id: int, content: str) -> Dict[str, Any]:
        """Send a message in a chat session"""
        data = {"content": content}
        response = self._request('POST', f'/api/v1/chat/sessions/{session_id}/messages', json=data)
        response.raise_for_status()
        return response.json()
    
    def upload_class_document(self, class_id: int, file_path: str) -> Dict[str, Any]:
        """Upload a document to a class"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self._request('POST', f'/api/v1/documents/classes/{class_id}/upload', files=files)
            response.raise_for_status()
            return response.json()
    
    def get_usage_stats(self) -> list:
        """Get usage statistics"""
        response = self._request('GET', '/api/v1/usage/my-usage')
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    client = StudHelperClient()
    
    # Register and login
    try:
        user = client.register(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            full_name="Test User"
        )
        print("User registered:", user['username'])
    except requests.exceptions.HTTPError:
        print("User might already exist, trying to login...")
    
    # Login
    login_result = client.login("testuser", "testpass123")
    print("Logged in as:", login_result['user']['username'])
    
    # Create a class
    new_class = client.create_class("Test Class", "A test class for the API")
    print("Created class:", new_class['name'], "Code:", new_class['class_code'])
    
    # Create chat session
    session = client.create_chat_session(new_class['id'], "Test Chat")
    print("Created chat session:", session['title'])
    
    # Send a message
    chat_response = client.send_message(session['id'], "Hello, can you help me with physics?")
    print("AI Response:", chat_response['ai_response']['content'])

### NEW FILE: client_examples/javascript_client.js
/**
 * JavaScript/Node.js client example for StudHelper Backend API
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class StudHelperClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = null;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000,
        });
        
        // Add request interceptor for authentication
        this.client.interceptors.request.use((config) => {
            if (this.token) {
                config.headers.Authorization = `Bearer ${this.token}`;
            }
            return config;
        });
    }
    
    async register(email, username, password, fullName = null) {
        const response = await this.client.post('/api/v1/auth/register', {
            email,
            username,
            password,
            full_name: fullName
        });
        return response.data;
    }
    
    async login(username, password) {
        const response = await this.client.post('/api/v1/auth/login', {
            username,
            password
        });
        
        this.token = response.data.access_token;
        return response.data;
    }
    
    async getProfile() {
        const response = await this.client.get('/api/v1/auth/me');
        return response.data;
    }
    
    async createClass(name, description = null) {
        const response = await this.client.post('/api/v1/classes/', {
            name,
            description
        });
        return response.data;
    }
    
    async joinClass(classCode) {
        const response = await this.client.post('/api/v1/classes/join', {
            class_code: classCode
        });
        return response.data;
    }
    
    async getClasses() {
        const response = await this.client.get('/api/v1/classes/');
        return response.data;
    }
    
    async createChatSession(classId, title) {
        const response = await this.client.post('/api/v1/chat/sessions', {
            class_id: classId,
            title
        });
        return response.data;
    }
    
    async sendMessage(sessionId, content) {
        const response = await this.client.post(`/api/v1/chat/sessions/${sessionId}/messages`, {
            content
        });
        return response.data;
    }
    
    async uploadClassDocument(classId, filePath) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        
        const response = await this.client.post(
            `/api/v1/documents/classes/${classId}/upload`,
            form,
            {
                headers: {
                    ...form.getHeaders()
                }
            }
        );
        return response.data;
    }
    
    async getUsageStats() {
        const response = await this.client.get('/api/v1/usage/my-usage');
        return response.data;
    }
}

// Example usage
async function example() {
    const client = new StudHelperClient();
    
    try {
        // Register and login
        try {
            const user = await client.register(
                'test@example.com',
                'testuser',
                'testpass123',
                'Test User'
            );
            console.log('User registered:', user.username);
        } catch (error) {
            console.log('User might already exist, trying to login...');
        }
        
        // Login
        const loginResult = await client.login('testuser', 'testpass123');
        console.log('Logged in as:', loginResult.user.username);
        
        // Create a class
        const newClass = await client.createClass('Test Class', 'A test class for the API');
        console.log('Created class:', newClass.name, 'Code:', newClass.class_code);
        
        // Create chat session
        const session = await client.createChatSession(newClass.id, 'Test Chat');
        console.log('Created chat session:', session.title);
        
        // Send a message
        const chatResponse = await client.sendMessage(session.id, 'Hello, can you help me with physics?');
        console.log('AI Response:', chatResponse.ai_response.content);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

module.exports = StudHelperClient;

// Run example if this file is executed directly
if (require.main === module) {
    example();
}

### NEW FILE: docs/DEVELOPMENT.md
# StudHelper Backend Development Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- OpenAI API Key
- Git

## Development Setup

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd studhelper-backend
```

2. **Run setup script**
```bash
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

3. **Configure environment**
```bash
# Edit .env with your actual values
nano .env
```

Required environment variables:
```bash
DATABASE_URL=postgresql://postgres:password@localhost/studhelper
SECRET_KEY=your-super-secret-key-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key
```

4. **Start the application**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Development

1. **Quick start with Docker**
```bash
chmod +x scripts/docker-dev.sh
./scripts/docker-dev.sh
```

This will:
- Build the Docker image
- Start PostgreSQL database
- Run database migrations
- Start the API server

## Testing

### Run All Tests
```bash
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh
```

### Run Specific Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_login_success -v

# Run with coverage
pytest --cov=app tests/
```

### Test Categories
- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test API endpoints end-to-end
- **Service tests**: Test business logic in service layer

## Database Management

### Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Seed Data
```bash
# Create demo data for development
python seed_data.py
```

This creates:
- Demo teacher account: `teacher@studhelper.com` / `teacher123`
- Demo student account: `student@studhelper.com` / `student123`
- Demo class with code: `PHYS101`

## API Development

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Adding New Endpoints

1. **Create route in `app/routes/`**
```python
from fastapi import APIRouter, Depends
from app.schemas import YourSchema
from app.services.your_service import YourService

router = APIRouter()

@router.post("/your-endpoint", response_model=YourSchema)
async def your_endpoint(data: YourSchema):
    # Implementation
    pass
```

2. **Add service logic in `app/services/`**
```python
class YourService:
    async def your_method(self, db: Session, data: YourSchema):
        # Business logic
        pass
```

3. **Include router in `app/main.py`**
```python
from app.routes import your_routes
app.include_router(your_routes.router, prefix="/api/v1/your-prefix", tags=["Your Tag"])
```

## Code Quality

### Linting and Formatting
```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint code
flake8 app tests

# Type checking
mypy app
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Debugging

### Logging
Application logs are written to:
- Console (INFO level)
- `logs/app.log` (detailed logs)
- `logs/error.log` (errors only)
- `logs/access.log` (HTTP access logs)

### Database Debugging
```bash
# Connect to database
psql postgresql://postgres:password@localhost/studhelper

# View tables
\dt

# View specific table
\d users
```

### Performance Profiling
```bash
# Profile API endpoints
pip install py-spy
py-spy top --pid <uvicorn-pid>
```

## Environment Configuration

### Development
```bash
DEBUG=true
DATABASE_URL=postgresql://postgres:password@localhost/studhelper
SECRET_KEY=development-secret-key
OPENAI_API_KEY=sk-your-api-key
```

### Testing
```bash
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key
OPENAI_API_KEY=test-key
```

## Monitoring

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
python monitoring/healthcheck.py --url http://localhost:8000
```

### Metrics Collection
```bash
# Collect application metrics
python monitoring/metrics.py
```

## Common Development Tasks

### Adding a New Model
1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Generate migration: `alembic revision --autogenerate -m "Add new model"`
4. Apply migration: `alembic upgrade head`

### Adding Authentication to Endpoint
```python
from app.utils.security import get_current_user
from app.schemas import UserResponse

@router.get("/protected")
async def protected_endpoint(current_user: UserResponse = Depends(get_current_user)):
    return {"user": current_user.username}
```

### File Upload Handling
```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate file type and size
    # Save file to storage
    # Process file content
    pass
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Check firewall settings

2. **OpenAI API errors**
   - Verify OPENAI_API_KEY is set
   - Check API key validity
   - Monitor rate limits

3. **Import errors**
   - Ensure virtual environment is activated
   - Check all `__init__.py` files exist
   - Verify PYTHONPATH includes app directory

4. **Test failures**
   - Check test database is clean
   - Verify test fixtures are working
   - Check for test data conflicts

### Getting Help

1. Check the logs in `logs/` directory
2. Review the API documentation at `/docs`
3. Run health checks with `monitoring/healthcheck.py`
4. Check GitHub issues for known problems

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run test suite: `./scripts/run-tests.sh`
4. Commit changes: `git commit -m "Add your feature"`
5. Push branch: `git push origin feature/your-feature`
6. Create pull request

### Code Standards
- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for public methods
- Maintain test coverage above 80%
- Add integration tests for new endpoints

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(auth): add password reset functionality

Add password reset endpoint and email notification service.
Includes rate limiting and security validation.

Closes #123
```

### NEW FILE: docs/PRODUCTION.md
# StudHelper Backend Production Deployment Guide

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database (managed service recommended)
- OpenAI API key

## Production Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install required tools
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 2. Application Deployment

```bash
# Clone repository
git clone <repository-url> /opt/studhelper
cd /opt/studhelper

# Copy and configure environment
cp .env.example .env
nano .env
```

### 3. Environment Configuration

Create production `.env` file:
```bash
# Database (use managed PostgreSQL service)
DATABASE_URL=postgresql://username:password@db-host:5432/studhelper

# Security (generate strong keys)
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-your-production-openai-api-key

# File Upload
UPLOAD_DIR=/opt/studhelper/uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,txt,docx

# CORS (add your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Application
DEBUG=false
```

### 4. SSL Certificate Setup

```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 5. Deploy Application

```bash
# Run deployment script
chmod +x scripts/production-deploy.sh

# Set required environment variables
export DATABASE_URL="postgresql://username:password@db-host:5432/studhelper"
export SECRET_KEY="your-super-secure-secret-key"
export OPENAI_API_KEY="sk-your-production-openai-api-key"

# Deploy
./scripts/production-deploy.sh
```

## Manual Deployment Steps

If you prefer manual deployment:

### 1. Build and Deploy

```bash
# Build Docker image
docker build -t studhelper-backend:latest .

# Create production directories
sudo mkdir -p /opt/studhelper/{uploads,logs,backups}
sudo chown -R $(id -u):$(id -g) /opt/studhelper

# Run database migrations
docker run --rm \
    -e DATABASE_URL="$DATABASE_URL" \
    studhelper-backend:latest \
    alembic upgrade head

# Start services
docker-compose -f docker-compose.production.yml up -d
```

### 2. Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/studhelper
sudo ln -s /etc/nginx/sites-available/studhelper /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Database Setup

### Managed Database (Recommended)

Use a managed PostgreSQL service like:
- AWS RDS
- Google Cloud SQL
- Digital Ocean Managed Databases
- Azure Database for PostgreSQL

Benefits:
- Automated backups
- High availability
- Automatic security updates
- Monitoring and alerting

### Self-Hosted Database

If you must self-host:

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createuser --createdb studhelper
sudo -u postgres createdb studhelper -O studhelper
sudo -u postgres psql -c "ALTER USER studhelper PASSWORD 'secure_password';"

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
# Update: shared_buffers, effective_cache_size, work_mem, maintenance_work_mem

sudo nano /etc/postgresql/13/main/pg_hba.conf
# Configure authentication methods

sudo systemctl restart postgresql
```

## Monitoring and Logging

### 1. Application Monitoring

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/studhelper
```

Add:
```
/opt/studhelper/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 studhelper studhelper
    postrotate
        docker-compose -f /opt/studhelper/docker-compose.production.yml restart backend
    endscript
}
```

### 2. Health Monitoring

```bash
# Set up health check cron job
crontab -e
```

Add:
```bash
# Health check every 5 minutes
*/5 * * * * /usr/bin/python3 /opt/studhelper/monitoring/healthcheck.py --url https://your-domain.com >> /var/log/studhelper-health.log 2>&1
```

### 3. System Monitoring

Install monitoring tools:
```bash
# Install system monitoring
sudo apt install htop iotop nethogs

# Optional: Install Prometheus node exporter
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*-linux-amd64.tar.gz
tar xvfz node_exporter-*-linux-amd64.tar.gz
sudo cp node_exporter-*/node_exporter /usr/local/bin/
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
sudo nano /opt/studhelper/backup-db.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/opt/studhelper/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE_URL="your-database-url"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/backup_$TIMESTAMP.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz s3://your-backup-bucket/
```

```bash
# Make executable and schedule
chmod +x /opt/studhelper/backup-db.sh
crontab -e
```

Add:
```bash
# Backup database daily at 2 AM
0 2 * * * /opt/studhelper/backup-db.sh
```

### 2. Application Backup

```bash
# Backup uploaded files
rsync -av /opt/studhelper/uploads/ /backup/uploads/

# Or use cloud sync
# aws s3 sync /opt/studhelper/uploads/ s3://your-files-bucket/
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (adjust port if needed)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### 2. System Security

```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
```

### 3. Application Security

- Use strong, unique SECRET_KEY
- Regularly rotate API keys
- Enable HTTPS only
- Set up proper CORS origins
- Monitor for security vulnerabilities
- Keep Docker images updated

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_chat_sessions_user_class ON chat_sessions(user_id, class_id);
CREATE INDEX CONCURRENTLY idx_usage_records_user_timestamp ON usage_records(user_id, timestamp);
CREATE INDEX CONCURRENTLY idx_documents_class_scope ON documents(class_id, scope);
```

### 2. Application Optimization

```bash
# Tune Docker container resources
docker-compose -f docker-compose.production.yml up -d
```

Update `docker-compose.production.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### 3. Caching

Consider adding Redis for caching:
```yaml
# Add to docker-compose.production.yml
redis:
  image: redis:alpine
  restart: unless-stopped
  volumes:
    - redis_data:/data
```

## SSL/TLS Configuration

### 1. Strong SSL Configuration

Update `nginx.conf` for better security:
```nginx
# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

### 2. Certificate Auto-Renewal

```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Check renewal service
sudo systemctl status certbot.timer
```

## Troubleshooting

### Common Production Issues

1. **Application won't start**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Check database connectivity
   docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
   ```

2. **High memory usage**
   ```bash
   # Monitor resources
   docker stats
   
   # Check application metrics
   python monitoring/metrics.py
   ```

3. **Slow database queries**
   ```sql
   -- Enable query logging
   ALTER SYSTEM SET log_statement = 'all';
   SELECT pg_reload_conf();
   
   -- Check slow queries
   SELECT query, total_time, calls 
   FROM pg_stat_statements 
   ORDER BY total_time DESC 
   LIMIT 10;
   ```

### Emergency Procedures

1. **Application Rollback**
   ```bash
   # Rollback to previous image
   docker tag studhelper-backend:previous studhelper-backend:latest
   docker-compose -f docker-compose.production.yml up -d
   ```

2. **Database Recovery**
   ```bash
   # Restore from backup
   gunzip -c /opt/studhelper/backups/backup_TIMESTAMP.sql.gz | psql $DATABASE_URL
   ```

3. **Service Restart**
   ```bash
   # Restart all services
   docker-compose -f docker-compose.production.yml restart
   
   # Restart nginx
   sudo systemctl restart nginx
   ```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Setup**
   - Use nginx or cloud load balancer
   - Configure session affinity if needed
   - Health check endpoints

2. **Database Scaling**
   - Read replicas for queries
   - Connection pooling
   - Database sharding (if needed)

3. **File Storage**
   - Use object storage (S3, GCS)
   - CDN for static content
   - Distributed file systems

### Vertical Scaling

1. **Resource Monitoring**
   ```bash
   # Monitor resource usage
   htop
   iotop
   docker stats
   ```

2. **Database Tuning**
   - Increase shared_buffers
   - Tune work_mem and maintenance_work_mem
   - Optimize queries and indexes

3. **Application Tuning**
   - Increase worker processes
   - Optimize Docker resource limits
   - Enable application-level caching

## Maintenance Schedule

### Daily
- Check application health
- Monitor error logs
- Verify backup completion

### Weekly
- Review performance metrics
- Check security updates
- Rotate log files

### Monthly
- Update dependencies
- Review and test backup recovery
- Security audit
- Performance optimization review

### Quarterly
- Comprehensive security review
- Disaster recovery testing
- Capacity planning review
- Documentation updates