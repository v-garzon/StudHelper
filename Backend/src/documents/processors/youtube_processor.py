"""YouTube video processor."""

import asyncio
import logging
import tempfile
import whisper
import yt_dlp
from pathlib import Path
from typing import Dict, List, Any, Optional

from openai import AsyncOpenAI

from .base import DocumentProcessor
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class YouTubeProcessor(DocumentProcessor):
    """YouTube video processor."""
    
    def __init__(self):
        super().__init__()
        self.supported_types = ["youtube", "video/youtube"]
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._whisper_model = None
    
    async def process(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process YouTube video and extract transcript."""
        try:
            # Get video metadata
            video_metadata = await self._get_video_metadata(url)
            
            # Download audio
            audio_path = await self._download_audio(url)
            
            try:
                # Transcribe audio (use local Whisper by default)
                transcript = await self._transcribe_with_local_whisper(audio_path)
                
                # Create chunks from transcript
                chunks = self._create_transcript_chunks(transcript, video_metadata)
                
                result = {
                    "success": True,
                    "chunks": chunks,
                    "metadata": {
                        **video_metadata,
                        "extraction_method": "whisper_local",
                        "word_count": len(transcript.get("text", "").split()),
                    },
                    "file_type": "youtube",
                    "processor": "YouTubeProcessor",
                }
                
                return result
                
            finally:
                # Clean up audio file
                if audio_path.exists():
                    audio_path.unlink()
            
        except Exception as e:
            logger.error(f"YouTube processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "chunks": [],
                "metadata": {"file_type": "youtube", "error": str(e)},
            }
    
    async def _download_audio(self, url: str) -> Path:
        """Download audio from YouTube video."""
        def download():
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_path = Path(tmp_file.name)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_path.with_suffix('.%(ext)s')),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return output_path.with_suffix('.wav')
        
        return await self._run_in_thread(download)
    
    async def _get_video_metadata(self, url: str) -> Dict[str, Any]:
        """Extract video metadata."""
        def extract_metadata():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get('title', ''),
                    "description": info.get('description', ''),
                    "duration": info.get('duration', 0),
                    "uploader": info.get('uploader', ''),
                    "upload_date": info.get('upload_date', ''),
                    "view_count": info.get('view_count', 0),
                    "url": url,
                }
        
        return await self._run_in_thread(extract_metadata)
    
    async def _transcribe_with_local_whisper(self, audio_path: Path) -> Dict[str, Any]:
        """Transcribe using local Whisper model."""
        def transcribe():
            if self._whisper_model is None:
                self._whisper_model = whisper.load_model("base")
            
            result = self._whisper_model.transcribe(
                str(audio_path),
                word_timestamps=True
            )
            return result
        
        return await self._run_in_thread(transcribe)
    
    async def _transcribe_with_openai(self, audio_path: Path) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API."""
        with open(audio_path, 'rb') as audio_file:
            transcript = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return {
            "text": transcript.text,
            "segments": getattr(transcript, 'segments', [])
        }
    
    def _create_transcript_chunks(
        self,
        transcript: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create searchable chunks from transcript."""
        chunks = []
        
        # If we have segments with timestamps, create time-based chunks
        if 'segments' in transcript and transcript['segments']:
            for i, segment in enumerate(transcript['segments']):
                content = segment.get('text', '').strip()
                if content:
                    chunks.append({
                        "content": content,
                        "metadata": self._create_chunk_metadata(
                            source=metadata.get("url", "youtube"),
                            chunk_index=i,
                            start_time=segment.get('start', 0),
                            end_time=segment.get('end', 0),
                            title=metadata.get("title", ""),
                            uploader=metadata.get("uploader", ""),
                            content_type="transcript_segment",
                        ),
                    })
        else:
            # Fall back to simple text chunking
            text = transcript.get('text', '')
            if text:
                # Split into chunks of roughly 750 words (5 minutes of speech)
                words = text.split()
                chunk_size = 750
                
                for i in range(0, len(words), chunk_size):
                    chunk_words = words[i:i + chunk_size]
                    chunk_text = " ".join(chunk_words)
                    
                    chunks.append({
                        "content": chunk_text,
                        "metadata": self._create_chunk_metadata(
                            source=metadata.get("url", "youtube"),
                            chunk_index=i // chunk_size,
                            title=metadata.get("title", ""),
                            uploader=metadata.get("uploader", ""),
                            content_type="transcript_chunk",
                        ),
                    })
        
        return chunks

