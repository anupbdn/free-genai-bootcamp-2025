from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.study_activity_service import StudyActivityService
from ..schemas.study_activity import StudyActivity, StudyActivityCreate, StudyActivityDetail

router = APIRouter()

@router.get("/study_activities", response_model=List[StudyActivity])
async def get_study_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return await StudyActivityService.get_study_activities(db, skip, limit)

@router.get("/study_activities/{activity_id}", response_model=StudyActivityDetail)
async def get_study_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = await StudyActivityService.get_study_activity(db, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Study activity not found")
    return activity 