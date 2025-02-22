from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StudyActivityBase(BaseModel):
    name: str = Field(..., description="Name of the activity")
    type: str = Field(..., description="Type of activity (e.g., flashcards)")

class StudyActivityCreate(StudyActivityBase):
    pass

class StudyActivity(StudyActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StudyActivityDetail(StudyActivity):
    total_sessions: int = 0
    average_success_rate: float = 0.0 