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

TEST_DB_PATH = "./test.db"

os.remove(TEST_DB_PATH) if os.path.exists(TEST_DB_PATH) else None

# Test database URL
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

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
    
    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)
    
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

