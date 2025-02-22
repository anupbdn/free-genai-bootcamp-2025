from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.study_session import StudySession
from ..schemas.study_session import StudySessionCreate

class StudySessionService:
    @staticmethod
    async def get_study_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[StudySession]:
        return db.query(StudySession).offset(skip).limit(limit).all()

    @staticmethod
    async def get_study_session(db: Session, session_id: int) -> Optional[StudySession]:
        return db.query(StudySession).filter(StudySession.id == session_id).first()

    @staticmethod
    async def create_study_session(db: Session, session: StudySessionCreate) -> StudySession:
        db_session = StudySession(**session.dict())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session 