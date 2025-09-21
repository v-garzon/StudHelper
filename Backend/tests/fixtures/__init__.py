"""Test fixtures for StudHelper backend."""

import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List

# Common test data
SAMPLE_USERS = [
    {
        "email": "alice@example.com",
        "username": "alice",
        "password": "alice123",
        "full_name": "Alice Johnson"
    },
    {
        "email": "bob@example.com", 
        "username": "bob",
        "password": "bob123",
        "full_name": "Bob Smith"
    }
]

SAMPLE_DOCUMENTS = [
    {
        "filename": "study_guide.pdf",
        "content_type": "application/pdf",
        "content": "Sample study guide content for testing"
    },
    {
        "filename": "lecture_notes.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
        "content": "Sample lecture notes for testing"
    }
]

SAMPLE_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ"
]

SAMPLE_CHAT_MESSAGES = [
    {
        "message": "What is machine learning?",
        "mode": "economic"
    },
    {
        "message": "Explain the concept of neural networks",
        "mode": "standard"
    },
    {
        "message": "How do I solve this calculus problem step by step?",
        "mode": "turbo"
    }
]

def get_sample_pdf_content() -> bytes:
    """Get sample PDF content for testing."""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj

4 0 obj
<<
/Length 120
>>
stream
BT
/F1 12 Tf
100 700 Td
(This is a test PDF document for StudHelper.) Tj
0 -20 Td
(It contains sample content for testing document processing.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000306 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
476
%%EOF"""

