"""File handling utilities."""

import hashlib
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import aiofiles


async def save_uploaded_file(content: bytes, filename: str, upload_dir: str) -> Path:
    """Save uploaded file to disk."""
    # Create upload directory if it doesn't exist
    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    file_hash = hashlib.md5(content).hexdigest()[:8]
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{file_hash}{ext}"
    
    file_path = upload_path / unique_filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return file_path


def get_file_type(filename: str, content_type: Optional[str] = None) -> str:
    """Determine file type from filename and content type."""
    if content_type:
        return content_type
    
    # Guess from filename
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        return mime_type
    
    # Fall back to extension
    ext = Path(filename).suffix.lower()
    ext_mapping = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".txt": "text/plain",
        ".md": "text/markdown",
    }
    
    return ext_mapping.get(ext, "application/octet-stream")


def validate_file_size(file_size: int, max_size: int = 100_000_000) -> bool:
    """Validate file size."""
    return file_size <= max_size


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    import re
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[^\w\-_\. ]', '', filename)
    
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Limit length
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:90] + ext
    
    return sanitized


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


async def cleanup_temp_files(temp_dir: str, max_age_hours: int = 24):
    """Clean up temporary files older than max_age_hours."""
    import time
    
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in temp_path.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                except Exception:
                    pass  # Ignore errors, file might be in use

