from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# Use absolute imports
from models.schemas import Transcript, TranscriptChunk
# from language_listening_app.models.schemas import Transcript, TranscriptChunk
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP
# from language_listening_app.config.settings import CHUNK_SIZE, CHUNK_OVERLAP
import re
import uuid

class TranscriptProcessor:
    """Handles YouTube transcript extraction and processing"""
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
            r'youtube\.com\/embed\/([^&\n?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError("Invalid YouTube URL")

    @staticmethod
    def get_transcript(video_id: str, language: str = 'en') -> List[dict]:
        """Fetch transcript from YouTube"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return transcript
        except TranscriptsDisabled:
            raise ValueError("Transcripts are disabled for this video")
        except NoTranscriptFound:
            raise ValueError(f"No transcript found for language: {language}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
            
        words = text.split()
        chunks = []
        
        # If text is smaller than chunk size, return it as a single chunk
        if len(words) <= chunk_size:
            return [text]
            
        # Ensure overlap is less than chunk_size to prevent infinite loops
        effective_overlap = min(overlap, chunk_size - 1)
        
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            
            # If we've reached the end, break
            if end >= len(words):
                break
                
            start = end - effective_overlap
            
        return chunks

    def process_transcript(self, url: str, language: str = 'en') -> Transcript:
        """Process YouTube video transcript"""
        # Extract video ID
        video_id = self.extract_video_id(url)
        
        # Get transcript
        transcript_data = self.get_transcript(video_id, language)
        
        # Combine transcript segments
        full_text = ' '.join(segment['text'] for segment in transcript_data)
        
        # Create chunks
        chunks = self.chunk_text(full_text)
        
        # Create TranscriptChunk objects
        transcript_chunks = [
            TranscriptChunk(
                id=str(uuid.uuid4()),
                text=chunk,
                metadata={
                    'start_index': i * (CHUNK_SIZE - CHUNK_OVERLAP),
                    'end_index': i * (CHUNK_SIZE - CHUNK_OVERLAP) + len(chunk.split())
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # Create Transcript object
        return Transcript(
            video_id=video_id,
            language=language,
            chunks=transcript_chunks,
            metadata={
                'url': url,
                'total_chunks': len(transcript_chunks),
                'total_words': len(full_text.split())
            }
        ) 