"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


class TestDocumentEndpoints:
    """Test document API endpoints."""
    @pytest.mark.asyncio
    async def test_upload_and_process_document(self, client, auth_headers, sample_pdf_content, mock_openai):
        files = {"file": ("test.pdf", sample_pdf_content, "application/pdf")}
        response = await client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        document = response.json()
        document_id = document["id"]
        
        # Check document was created
        response = await client.get(
            f"/api/v1/documents/{document_id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["filename"] == "test.pdf"
    
    @pytest.mark.asyncio
    async def test_youtube_upload(self, client, auth_headers):
        """Test YouTube video upload."""
        response = await client.post(
            "/api/v1/documents/youtube",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Test Video"
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        document = response.json()
        assert document["file_type"] == "youtube"


class TestChatEndpoints:
    """Test chat API endpoints."""
    
    @pytest.mark.asyncio
    async def test_chat_message(self, client, auth_headers, mock_openai):
        """Test sending chat message."""
        response = await client.post(
            "/api/v1/ai/chat",
            json={
                "message": "Hello, how are you?",
                "mode": "economic",
                "include_context": False,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Mock AI response"
        assert data["mode"] == "economic"
        assert "session_id" in data
    
    @pytest.mark.asyncio
    async def test_get_chat_sessions(self, client, auth_headers):
        """Test getting chat sessions."""
        response = await client.get("/api/v1/ai/sessions", headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)