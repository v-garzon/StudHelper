"""Input validation utilities."""

import re
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator


class FileValidation:
    """File validation utilities."""
    
    ALLOWED_EXTENSIONS = {
        ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".md"
    }
    
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
        "text/plain",
        "text/markdown",
    }
    
    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """Validate file extension."""
        from pathlib import Path
        return Path(filename).suffix.lower() in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def validate_mime_type(cls, mime_type: str) -> bool:
        """Validate MIME type."""
        return mime_type in cls.ALLOWED_MIME_TYPES
    
    @classmethod
    def validate_file_size(cls, size: int, max_size: int = 100_000_000) -> bool:
        """Validate file size (default 100MB)."""
        return 0 < size <= max_size


class YouTubeValidation:
    """YouTube URL validation."""
    
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    @classmethod
    def validate_youtube_url(cls, url: str) -> bool:
        """Validate YouTube URL."""
        if not url:
            return False
        
        for pattern in cls.YOUTUBE_PATTERNS:
            if re.match(pattern, url.strip()):
                return True
        return False
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url.strip())
            if match:
                return match.group(1)
        return None


class TextValidation:
    """Text content validation."""
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 1, max_length: int = 10000) -> bool:
        """Validate text length."""
        return min_length <= len(text.strip()) <= max_length
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input."""
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}

        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        # Alphanumeric, underscores, hyphens, 3-30 characters
        pattern = r'^[a-zA-Z0-9_-]{3,30}

        return bool(re.match(pattern, username))


def validate_pagination(page: int = 1, page_size: int = 20, max_page_size: int = 100) -> tuple[int, int]:
    """Validate and normalize pagination parameters."""
    page = max(1, page)
    page_size = max(1, min(page_size, max_page_size))
    return page, page_size


