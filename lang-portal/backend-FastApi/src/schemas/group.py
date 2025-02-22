from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .word import Word

class GroupBase(BaseModel):
    name: str = Field(..., description="Name of the word group")

class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    word_count: Optional[int] = 0

    class Config:
        from_attributes = True

class GroupDetail(Group):
    words: List[Word] = []
    created_at: datetime
    total_words: int = 0
    study_sessions_count: int = 0 