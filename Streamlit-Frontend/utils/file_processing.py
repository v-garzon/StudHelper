

import streamlit as st
from typing import List, Dict, Any
import os
import tempfile
from datetime import datetime

def process_uploaded_files(uploaded_files) -> List[Dict[str, Any]]:
    """Process uploaded files and extract text content"""
    
    processed_files = []
    
    for file in uploaded_files:
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(file.getbuffer())
                tmp_path = tmp_file.name
            
            # Process based on file type
            file_info = {
                'name': file.name,
                'size': file.size,
                'type': file.type,
                'processed_at': datetime.now().isoformat()
            }
            
            if file.type == 'application/pdf':
                result = process_pdf_file(tmp_path, file_info)
            elif file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                result = process_word_file(tmp_path, file_info)
            elif file.type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                result = process_powerpoint_file(tmp_path, file_info)
            elif file.type == 'text/plain':
                result = process_text_file(tmp_path, file_info)
            elif file.type == 'text/markdown':
                result = process_markdown_file(tmp_path, file_info)
            else:
                result = {
                    **file_info,
                    'status': 'unsupported',
                    'error': f'Unsupported file type: {file.type}',
                    'content': '',
                    'pages': 0
                }
            
            processed_files.append(result)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
        except Exception as e:
            processed_files.append({
                **file_info,
                'status': 'error',
                'error': str(e),
                'content': '',
                'pages': 0
            })
    
    return processed_files

def process_pdf_file(file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Process PDF file and extract text"""
    
    try:
        # This is a placeholder implementation
        # In the real version, this would use PyPDF2 or pdfplumber
        
        # Simulate PDF processing
        import time
        time.sleep(0.5)  # Simulate processing time
        
        # Mock extracted content
        content = f"""
        This is extracted content from {file_info['name']}.
        
        Chapter 1: Introduction
        This chapter covers the basic concepts and foundational principles.
        
        Chapter 2: Advanced Topics  
        This section delves into more complex subject matter.
        
        Chapter 3: Practical Applications
        Here we explore real-world use cases and examples.
        
        Chapter 4: Conclusion
        Summary of key points and takeaways.
        """
        
        # Mock page count (would be actual in real implementation)
        pages = max(1, int(file_info['size'] / 50000))  # Rough estimate
        
        return {
            **file_info,
            'status': 'success',
            'content': content.strip(),
            'pages': pages,
            'word_count': len(content.split()),
            'file_type': 'pdf'
        }
        
    except Exception as e:
        return {
            **file_info,
            'status': 'error',
            'error': str(e),
            'content': '',
            'pages': 0,
            'file_type': 'pdf'
        }

def process_word_file(file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Process Word document and extract text"""
    
    try:
        # This is a placeholder implementation
        # In the real version, this would use python-docx
        
        import time
        time.sleep(0.3)
        
        content = f"""
        Content extracted from Word document: {file_info['name']}
        
        Document Overview:
        This document contains important information for your studies.
        
        Key Sections:
        - Executive Summary
        - Detailed Analysis  
        - Recommendations
        - Appendices
        
        The document provides comprehensive coverage of the subject matter
        with detailed explanations and supporting evidence.
        """
        
        pages = max(1, int(file_info['size'] / 30000))
        
        return {
            **file_info,
            'status': 'success',
            'content': content.strip(),
            'pages': pages,
            'word_count': len(content.split()),
            'file_type': 'word'
        }
        
    except Exception as e:
        return {
            **file_info,
            'status': 'error',
            'error': str(e),
            'content': '',
            'pages': 0,
            'file_type': 'word'
        }

def process_powerpoint_file(file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Process PowerPoint presentation and extract text"""
    
    try:
        # This is a placeholder implementation
        # In the real version, this would use python-pptx
        
        import time
        time.sleep(0.4)
        
        content = f"""
        Presentation content from: {file_info['name']}
        
        Slide 1: Title Slide
        Introduction to the topic
        
        Slide 2: Overview
        Main concepts and objectives
        
        Slide 3: Key Points
        • Important concept 1
        • Important concept 2  
        • Important concept 3
        
        Slide 4: Details
        Detailed explanation of each concept
        
        Slide 5: Examples
        Real-world applications and case studies
        
        Slide 6: Summary
        Key takeaways and conclusions
        """
        
        slides = max(1, int(file_info['size'] / 100000))
        
        return {
            **file_info,
            'status': 'success',
            'content': content.strip(),
            'pages': slides,
            'word_count': len(content.split()),
            'file_type': 'powerpoint',
            'slides': slides
        }
        
    except Exception as e:
        return {
            **file_info,
            'status': 'error',
            'error': str(e),
            'content': '',
            'pages': 0,
            'file_type': 'powerpoint'
        }

def process_text_file(file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Process plain text file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Estimate pages (roughly 500 words per page)
        word_count = len(content.split())
        pages = max(1, word_count // 500)
        
        return {
            **file_info,
            'status': 'success',
            'content': content,
            'pages': pages,
            'word_count': word_count,
            'file_type': 'text'
        }
        
    except Exception as e:
        return {
            **file_info,
            'status': 'error',
            'error': str(e),
            'content': '',
            'pages': 0,
            'file_type': 'text'
        }

def process_markdown_file(file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Process Markdown file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Estimate pages
        word_count = len(content.split())
        pages = max(1, word_count // 500)
        
        return {
            **file_info,
            'status': 'success',
            'content': content,
            'pages': pages,
            'word_count': word_count,
            'file_type': 'markdown'
        }
        
    except Exception as e:
        return {
            **file_info,
            'status': 'error',
            'error': str(e),
            'content': '',
            'pages': 0,
            'file_type': 'markdown'
        }

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to end at a sentence boundary
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        
        # Prevent infinite loop
        if start >= end:
            start = end
    
    return chunks

def estimate_processing_time(files: List) -> int:
    """Estimate processing time for uploaded files"""
    
    total_size = sum(file.size for file in files)
    
    # Rough estimates based on file size
    if total_size < 1_000_000:  # < 1MB
        return 10
    elif total_size < 10_000_000:  # < 10MB
        return 30
    elif total_size < 50_000_000:  # < 50MB
        return 60
    else:
        return 120

def validate_file_upload(files: List) -> Dict[str, Any]:
    """Validate uploaded files"""
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'total_size': 0,
        'file_count': len(files)
    }
    
    supported_types = {
        'application/pdf': 'PDF',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
        'text/plain': 'Text',
        'text/markdown': 'Markdown'
    }
    
    max_file_size = 50 * 1024 * 1024  # 50MB per file
    max_total_size = 100 * 1024 * 1024  # 100MB total
    
    total_size = 0
    
    for file in files:
        total_size += file.size
        
        # Check file type
        if file.type not in supported_types:
            validation_result['errors'].append(
                f"Unsupported file type: {file.name} ({file.type})"
            )
            validation_result['valid'] = False
        
        # Check individual file size
        if file.size > max_file_size:
            validation_result['errors'].append(
                f"File too large: {file.name} ({file.size / 1024 / 1024:.1f}MB > 50MB)"
            )
            validation_result['valid'] = False
        
        # Check for empty files
        if file.size == 0:
            validation_result['errors'].append(f"Empty file: {file.name}")
            validation_result['valid'] = False
    
    # Check total size
    validation_result['total_size'] = total_size
    
    if total_size > max_total_size:
        validation_result['errors'].append(
            f"Total upload size too large: {total_size / 1024 / 1024:.1f}MB > 100MB"
        )
        validation_result['valid'] = False
    
    # Warnings for large uploads
    if total_size > 25 * 1024 * 1024:  # 25MB
        validation_result['warnings'].append(
            "Large upload detected. Processing may take longer."
        )
    
    return validation_result

def get_supported_file_types() -> Dict[str, str]:
    """Get list of supported file types"""
    
    return {
        'pdf': 'PDF Documents',
        'docx': 'Word Documents',
        'pptx': 'PowerPoint Presentations',
        'txt': 'Text Files',
        'md': 'Markdown Files'
    }

