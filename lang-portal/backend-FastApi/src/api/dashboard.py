from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.dashboard_service import DashboardService
from ..schemas.dashboard import LastStudySession, StudyProgress, QuickStats

router = APIRouter()

@router.get("/dashboard/last_study_session", response_model=LastStudySession)
async def get_last_study_session(db: Session = Depends(get_db)):
    return await DashboardService.get_last_study_session(db)

@router.get("/dashboard/study_progress", response_model=StudyProgress)
async def get_study_progress(db: Session = Depends(get_db)):
    return await DashboardService.get_study_progress(db)

@router.get("/dashboard/quick-stats", response_model=QuickStats)
async def get_quick_stats(db: Session = Depends(get_db)):
    return await DashboardService.get_quick_stats(db) 