"""Configuration management for StudHelper frontend."""

import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # Backend API settings
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    API_BASE_URL: str = f"{BACKEND_URL}/api/v1"
    
    # API endpoints
    AUTH_LOGIN_URL: str = f"{API_BASE_URL}/auth/login"
    AUTH_REGISTER_URL: str = f"{API_BASE_URL}/auth/register"
    AUTH_ME_URL: str = f"{API_BASE_URL}/auth/me"
    
    DOCUMENTS_UPLOAD_URL: str = f"{API_BASE_URL}/documents/upload"
    DOCUMENTS_YOUTUBE_URL: str = f"{API_BASE_URL}/documents/youtube"
    DOCUMENTS_LIST_URL: str = f"{API_BASE_URL}/documents/"
    
    AI_CHAT_URL: str = f"{API_BASE_URL}/ai/chat"
    AI_CHAT_STREAM_URL: str = f"{API_BASE_URL}/ai/chat/stream"
    AI_SESSIONS_URL: str = f"{API_BASE_URL}/ai/sessions"
    
    RAG_SEARCH_URL: str = f"{API_BASE_URL}/rag/search"
    USAGE_ANALYTICS_URL: str = f"{API_BASE_URL}/usage/analytics"
    
    # Frontend settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FILE_TYPES: list = ['.pdf', '.docx', '.pptx', '.txt', '.md']
    
    # Session settings
    TOKEN_KEY: str = "studhelper_token"
    USER_KEY: str = "studhelper_user"
    
    @classmethod
    def get_headers(cls, token: Optional[str] = None) -> dict:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    @classmethod
    def get_file_headers(cls, token: Optional[str] = None) -> dict:
        """Get headers for file upload requests."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

