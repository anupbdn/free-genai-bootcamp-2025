from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TranscriptChunk(BaseModel):
    """Model for a chunk of transcript text"""
    id: str
    text: str
    index: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class Question(BaseModel):
    """Model for a generated question"""
    id: str
    text: str
    answer: str
    explanation: str
    difficulty: str
    context: str
    question_type: str = "comprehension"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class Transcript(BaseModel):
    """Model for a complete transcript"""
    video_id: str
    title: Optional[str] = None
    url: Optional[str] = None
    language: str
    chunks: List[TranscriptChunk]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class QuestionSet(BaseModel):
    """Model for a set of questions"""
    id: str
    transcript_id: str
    questions: List[Question]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now) 