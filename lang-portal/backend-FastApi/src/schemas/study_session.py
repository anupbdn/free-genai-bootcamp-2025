from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .word import WordWithStats

class StudySessionBase(BaseModel):
    group_id: int
    study_activity_id: int

class StudySessionCreate(StudySessionBase):
    pass

class StudySession(StudySessionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudySessionDetail(StudySession):
    words: List[WordWithStats] = []
    correct_count: int = 0
    total_count: int = 0 