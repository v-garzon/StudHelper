

import streamlit as st
import re
from typing import Optional, Dict, Any
from datetime import datetime

def is_valid_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL"""
    
    if not url:
        return False
    
    # YouTube URL patterns
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url.strip()):
            return True
    
    return False

def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    
    if not url:
        return None
    
    # YouTube URL patterns with capture groups
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1)
    
    return None

def get_youtube_video_info(url: str) -> Dict[str, Any]:
    """Get basic info about YouTube video (placeholder implementation)"""
    
    video_id = extract_youtube_id(url)
    
    if not video_id:
        return {
            'valid': False,
            'error': 'Invalid YouTube URL'
        }
    
    # This is a placeholder implementation
    # In a real implementation, you would use YouTube API or yt-dlp
    # to get actual video metadata
    
    try:
        # Simulate API call
        import time
        time.sleep(0.5)
        
        # Mock video info
        video_info = {
            'valid': True,
            'video_id': video_id,
            'url': url,
            'title': f'Educational Video {video_id[:8]}',
            'description': 'This is a placeholder description for the YouTube video.',
            'duration': '15:30',
            'duration_seconds': 930,
            'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
            'channel': 'Educational Channel',
            'view_count': '1,234,567',
            'upload_date': '2023-01-15',
            'language': 'en',
            'captions_available': True
        }
        
        return video_info
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error fetching video info: {str(e)}'
        }

def process_youtube_video(url: str) -> Dict[str, Any]:
    """Process YouTube video and extract transcript (placeholder)"""
    
    video_info = get_youtube_video_info(url)
    
    if not video_info['valid']:
        return video_info
    
    try:
        # This is a placeholder implementation
        # In real implementation, you would:
        # 1. Download audio using yt-dlp
        # 2. Transcribe using Whisper
        # 3. Process transcript text
        
        import time
        time.sleep(2)  # Simulate processing time
        
        # Mock transcript
        transcript = f"""
        [00:00] Welcome to this educational video about {video_info['title']}.
        
        [00:30] In this video, we'll cover the fundamental concepts and principles
        that are essential for understanding this topic.
        
        [02:15] First, let's start with the basic definitions and terminology.
        These concepts form the foundation of our understanding.
        
        [05:45] Now, let's dive deeper into the practical applications
        and real-world examples of these concepts.
        
        [08:20] It's important to understand how these principles
        connect to other areas of study and research.
        
        [11:30] Let's look at some case studies that demonstrate
        these concepts in action.
        
        [13:45] In conclusion, we've covered the key points including
        the main concepts, practical applications, and real-world examples.
        
        [14:50] Thank you for watching this educational content.
        Remember to review the key concepts we discussed.
        """
        
        # Process transcript into chunks
        chunks = chunk_transcript(transcript)
        
        result = {
            **video_info,
            'status': 'success',
            'transcript': transcript,
            'chunks': chunks,
            'word_count': len(transcript.split()),
            'processing_time': '2.3 seconds',
            'processed_at': datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        return {
            **video_info,
            'status': 'error',
            'error': f'Error processing video: {str(e)}'
        }

def chunk_transcript(transcript: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Split transcript into overlapping chunks"""
    
    if not transcript:
        return []
    
    # Remove timestamp markers for chunking
    clean_text = re.sub(r'\[\d{2}:\d{2}\]', '', transcript)
    clean_text = clean_text.strip()
    
    chunks = []
    start = 0
    
    while start < len(clean_text):
        end = start + chunk_size
        
        # Try to end at a sentence boundary
        if end < len(clean_text):
            for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                if clean_text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = clean_text[start:end].strip()
        if chunk:
            chunks.append({
                'text': chunk,
                'start_char': start,
                'end_char': end,
                'word_count': len(chunk.split())
            })
        
        start = end - overlap
        
        if start >= end:
            start = end
    
    return chunks

def validate_youtube_url(url: str) -> Dict[str, Any]:
    """Validate YouTube URL and return validation result"""
    
    result = {
        'valid': False,
        'error': None,
        'video_id': None,
        'url': url.strip() if url else ''
    }
    
    if not url or not url.strip():
        result['error'] = 'URL cannot be empty'
        return result
    
    # Check if it's a valid YouTube URL
    if not is_valid_youtube_url(url):
        result['error'] = 'Not a valid YouTube URL'
        return result
    
    # Extract video ID
    video_id = extract_youtube_id(url)
    if not video_id:
        result['error'] = 'Could not extract video ID'
        return result
    
    result['valid'] = True
    result['video_id'] = video_id
    
    return result

def get_youtube_thumbnail_url(video_id: str, quality: str = 'maxresdefault') -> str:
    """Get YouTube thumbnail URL"""
    
    valid_qualities = ['default', 'mqdefault', 'hqdefault', 'sddefault', 'maxresdefault']
    
    if quality not in valid_qualities:
        quality = 'maxresdefault'
    
    return f'https://img.youtube.com/vi/{video_id}/{quality}.jpg'

def format_duration(seconds: int) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS format"""
    
    if seconds < 3600:  # Less than 1 hour
        minutes = seconds // 60
        seconds = seconds % 60
        return f'{minutes:02d}:{seconds:02d}'
    else:  # 1 hour or more
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def estimate_transcript_length(duration_seconds: int) -> int:
    """Estimate transcript word count based on video duration"""
    
    # Rough estimate: 150-200 words per minute for educational content
    words_per_minute = 175
    minutes = duration_seconds / 60
    estimated_words = int(minutes * words_per_minute)
    
    return estimated_words

def get_supported_youtube_formats() -> list:
    """Get list of supported YouTube URL formats"""
    
    return [
        'https://www.youtube.com/watch?v=VIDEO_ID',
        'https://youtu.be/VIDEO_ID',
        'https://www.youtube.com/embed/VIDEO_ID',
        'https://www.youtube.com/v/VIDEO_ID'
    ]

def extract_timestamps_from_transcript(transcript: str) -> list:
    """Extract timestamps from transcript text"""
    
    timestamps = []
    
    # Find timestamp patterns like [MM:SS] or [HH:MM:SS]
    timestamp_pattern = r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]'
    
    matches = re.finditer(timestamp_pattern, transcript)
    
    for match in matches:
        timestamp_str = match.group(1)
        start_pos = match.start()
        end_pos = match.end()
        
        timestamps.append({
            'timestamp': timestamp_str,
            'position': start_pos,
            'end_position': end_pos
        })
    
    return timestamps

def clean_transcript_text(transcript: str) -> str:
    """Clean transcript text by removing timestamps and formatting"""
    
    # Remove timestamp markers
    clean_text = re.sub(r'\[\d{1,2}:\d{2}(?::\d{2})?\]', '', transcript)
    
    # Clean up extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # Remove extra newlines
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
    
    return clean_text.strip()

