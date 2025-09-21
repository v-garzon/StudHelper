"""Document-related test fixtures."""

import tempfile
from pathlib import Path
from typing import Dict, Any, List, BinaryIO
import zipfile
import xml.etree.ElementTree as ET


class DocumentFixtures:
    """Document test fixtures generator."""
    
    @staticmethod
    def create_sample_pdf() -> bytes:
        """Create a minimal valid PDF for testing."""
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
/Length 200
>>
stream
BT
/F1 12 Tf
50 750 Td
(StudHelper Test Document) Tj
0 -30 Td
(This is a sample PDF document created for testing purposes.) Tj
0 -20 Td
(It contains multiple lines of text to test text extraction.) Tj
0 -20 Td
(The document processing system should extract this content.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000356 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
606
%%EOF"""
    
    @staticmethod
    def create_sample_docx() -> bytes:
        """Create a minimal valid DOCX for testing."""
        # Create a temporary DOCX file
        with tempfile.NamedTemporaryFile(suffix='.docx') as tmp_file:
            with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as docx:
                # Create content types
                content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
                docx.writestr('[Content_Types].xml', content_types)
                
                # Create relationships
                rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
                docx.writestr('_rels/.rels', rels)
                
                # Create document content
                document = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>StudHelper Test Document</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>This is a sample Word document for testing the document processing capabilities.</w:t>
            </w:r>
        </w:p>
        <w:p>
            <w:r>
                <w:t>The system should be able to extract text from this DOCX file.</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''
                docx.writestr('word/document.xml', document)
            
            tmp_file.seek(0)
            return tmp_file.read()
    
    @staticmethod
    def create_sample_text() -> str:
        """Create sample text content."""
        return """StudHelper Test Document

Introduction
============

This is a comprehensive test document for the StudHelper AI study assistant system.
The document contains various types of content to test different processing capabilities.

Chapter 1: Machine Learning Basics
==================================

Machine learning is a subset of artificial intelligence that focuses on the development
of algorithms that can learn and make decisions from data without being explicitly programmed.

Key concepts include:
- Supervised learning
- Unsupervised learning  
- Reinforcement learning
- Neural networks
- Deep learning

Chapter 2: Natural Language Processing
=====================================

Natural Language Processing (NLP) is a field of AI that deals with the interaction
between computers and human language. It involves:

1. Text preprocessing
2. Tokenization
3. Part-of-speech tagging
4. Named entity recognition
5. Sentiment analysis

Example Code:
```python
def tokenize_text(text):
    return text.split()

tokens = tokenize_text("Hello world")
print(tokens)  # ['Hello', 'world']
```

Conclusion
==========

This document demonstrates various content types that the StudHelper system
should be able to process and understand for effective AI assistance.

Tables and Lists
===============

Here's a sample table:

| Algorithm | Type | Use Case |
|-----------|------|----------|
| Linear Regression | Supervised | Prediction |
| K-Means | Unsupervised | Clustering |
| Q-Learning | Reinforcement | Game AI |

Bullet points:
• First point about AI
• Second point about ML
• Third point about NLP

Numbered list:
1. Data collection
2. Data preprocessing  
3. Model training
4. Model evaluation
5. Deployment

Mathematical Concepts
==================

The document also includes mathematical notation:
- Linear function: y = mx + b
- Quadratic function: y = ax² + bx + c
- Derivative: f'(x) = lim(h→0) [f(x+h) - f(x)]/h

This content should be properly extracted and made searchable by the RAG system.
"""
    
    @staticmethod
    def get_sample_file_data() -> List[Dict[str, Any]]:
        """Get sample file data for testing uploads."""
        return [
            {
                "filename": "test_document.pdf",
                "content": DocumentFixtures.create_sample_pdf(),
                "content_type": "application/pdf",
                "description": "Sample PDF for testing"
            },
            {
                "filename": "test_document.docx", 
                "content": DocumentFixtures.create_sample_docx(),
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Sample DOCX for testing"
            },
            {
                "filename": "test_document.txt",
                "content": DocumentFixtures.create_sample_text().encode('utf-8'),
                "content_type": "text/plain",
                "description": "Sample text file for testing"
            }
        ]
    
    @staticmethod
    def create_corrupted_pdf() -> bytes:
        """Create a corrupted PDF for error testing."""
        return b"Not a real PDF file - this should cause an error"
    
    @staticmethod
    def create_large_text_document(size_kb: int = 100) -> str:
        """Create a large text document for performance testing."""
        base_text = DocumentFixtures.create_sample_text()
        repetitions = (size_kb * 1024) // len(base_text.encode('utf-8')) + 1
        return (base_text + "\n\n") * repetitions

