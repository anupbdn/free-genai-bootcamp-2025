from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class WordBase(BaseModel):
    japanese: str = Field(..., description="Japanese word/phrase")
    romaji: str = Field(..., description="Romanized version")
    english: str = Field(..., description="English translation")
    parts: Optional[Dict] = Field(None, description="Word components (kanji, hiragana, etc.)")

class WordCreate(WordBase):
    pass

class WordUpdate(WordBase):
    pass

class Word(WordBase):
    id: int
    
    class Config:
        from_attributes = True

class WordInDB(Word):
    pass

class WordWithStats(Word):
    correct_count: int = 0
    wrong_count: int = 0
    success_rate: float = 0.0
    last_reviewed: Optional[datetime] = None 