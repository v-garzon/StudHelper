"""End-to-end workflow tests."""

import pytest
from httpx import AsyncClient


class TestCompleteWorkflow:
    """Test complete application workflows."""
    
    async def test_study_session_workflow(
        self,
        client: AsyncClient,
        auth_headers,
        sample_pdf_content,
        mock_openai,
    ):
        """Test complete study session workflow."""
        # 1. Upload document
        files = {"file": ("study_material.pdf", sample_pdf_content, "application/pdf")}
        upload_response = await client.post(
            "/api/v1/documents/upload",
            files=files,
            headers=auth_headers,
        )
        assert upload_response.status_code == 201
        
        # 2. Wait for processing (in real scenario)
        # For tests, we'll assume processing completes
        
        # 3. Search documents
        search_response = await client.post(
            "/api/v1/rag/search",
            json={
                "query": "test content",
                "limit": 5,
            },
            headers=auth_headers,
        )
        assert search_response.status_code == 200
        
        # 4. Chat about the document
        chat_response = await client.post(
            "/api/v1/ai/chat",
            json={
                "message": "What can you tell me about this document?",
                "mode": "standard",
                "include_context": True,
            },
            headers=auth_headers,
        )
        assert chat_response.status_code == 200
        
        # 5. Check usage statistics
        usage_response = await client.get(
            "/api/v1/usage/analytics?days=1",
            headers=auth_headers,
        )
        assert usage_response.status_code == 200
        usage_data = usage_response.json()
        assert usage_data["total_requests"] > 0


