import pytest
from unittest.mock import patch, AsyncMock

def test_create_chat_session(client, auth_headers_student, test_user, test_class, test_db):
    """Test creating a chat session"""
    # First enroll student in class
    from app.models import ClassMembership
    enrollment = ClassMembership(
        user_id=test_user.id,  # Use actual user ID, not hardcoded 1
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
    assert response.status_code == 201, f"Response: {response.status_code}, {response.text}"
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
def test_send_message(mock_generate, client, auth_headers_student, test_user, test_class, test_db):
    """Test sending a message in a chat session"""
    # Setup enrollment and session
    from app.models import ClassMembership, ChatSession
    enrollment = ClassMembership(
        user_id=test_user.id,  # Use actual user ID
        class_id=test_class.id,
        can_chat=True
    )
    test_db.add(enrollment)
    test_db.commit()
    
    session = ChatSession(
        title="Test Session",
        user_id=test_user.id,  # Use actual user ID
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
    assert response.status_code == 200, f"Response: {response.status_code}, {response.text}"
    data = response.json()
    assert data["user_message"]["content"] == message_data["content"]
    assert data["ai_response"]["content"] == "This is a test AI response"

def test_get_session_messages(client, auth_headers_student, test_user, test_class, test_db):
    """Test getting messages from a session"""
    # Create session
    from app.models import ChatSession
    session = ChatSession(
        title="Test Session",
        user_id=test_user.id,  # Use actual user ID
        class_id=test_class.id
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    
    response = client.get(
        f"/api/v1/chat/sessions/{session.id}/messages",
        headers=auth_headers_student
    )
    assert response.status_code == 200, f"Response: {response.status_code}, {response.text}"
    messages = response.json()
    assert isinstance(messages, list)

