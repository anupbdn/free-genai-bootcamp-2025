from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LastStudySession(BaseModel):
    id: int
    group_id: int
    created_at: datetime
    study_activity_id: int
    group_name: str

class StudyProgress(BaseModel):
    total_words_studied: int
    total_available_words: int

class QuickStats(BaseModel):
    success_rate: float
    total_study_sessions: int
    total_active_groups: int
    study_streak_days: int 