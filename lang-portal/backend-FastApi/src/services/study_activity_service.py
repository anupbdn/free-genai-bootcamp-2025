from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.study_activity import StudyActivity
from ..schemas.study_activity import StudyActivityCreate

class StudyActivityService:
    @staticmethod
    async def get_study_activities(db: Session, skip: int = 0, limit: int = 100) -> List[StudyActivity]:
        return db.query(StudyActivity).offset(skip).limit(limit).all()

    @staticmethod
    async def get_study_activity(db: Session, activity_id: int) -> Optional[StudyActivity]:
        return db.query(StudyActivity).filter(StudyActivity.id == activity_id).first()

    @staticmethod
    async def create_study_activity(db: Session, activity: StudyActivityCreate) -> StudyActivity:
        db_activity = StudyActivity(**activity.dict())
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity 