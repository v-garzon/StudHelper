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

