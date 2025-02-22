from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from ..models.study_session import StudySession
from ..models.word_review import WordReviewItem
from ..models.word import Word

class DashboardService:
    @staticmethod
    async def get_last_study_session(db: Session):
        return db.query(StudySession).order_by(StudySession.created_at.desc()).first()

    @staticmethod
    async def get_study_progress(db: Session):
        total_words = db.query(func.count(Word.id)).scalar()
        studied_words = db.query(func.count(WordReviewItem.word_id.distinct())).scalar()
        
        return {
            "total_words_studied": studied_words,
            "total_available_words": total_words
        }

    @staticmethod
    async def get_quick_stats(db: Session):
        total_sessions = db.query(func.count(StudySession.id)).scalar()
        correct_reviews = db.query(WordReviewItem).filter(WordReviewItem.correct == True).count()
        total_reviews = db.query(WordReviewItem).count()
        success_rate = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            "success_rate": success_rate,
            "total_study_sessions": total_sessions,
            "total_active_groups": db.query(func.count(StudySession.group_id.distinct())).scalar(),
            "study_streak_days": 0  # To be implemented with actual streak calculation
        } 