from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.dashboard_service import DashboardService
from ..schemas.dashboard import LastStudySession, StudyProgress, QuickStats
from ..services.study_session_service import StudySessionService

router = APIRouter()

@router.get("/dashboard/last_study_session")
async def get_last_study_session(db: Session = Depends(get_db)):
    try:
        session = await StudySessionService.get_latest_session(db)
        if not session:
            return {
                "group_name": "No sessions yet",
                "activity": {"name": "N/A"},
                "stats": {
                    "words_reviewed": 0,
                    "correct_answers": 0,
                    "incorrect_answers": 0,
                    "completion_rate": 0
                }
            }
        return session
    except Exception as e:
        print(f"Error in get_last_study_session: {e}")
        return {
            "group_name": "Error loading session",
            "activity": {"name": "Error"},
            "stats": {
                "words_reviewed": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "completion_rate": 0
            }
        }

@router.get("/dashboard/study_progress", response_model=StudyProgress)
async def get_study_progress(db: Session = Depends(get_db)):
    return await DashboardService.get_study_progress(db)

@router.get("/dashboard/quick-stats", response_model=QuickStats)
async def get_quick_stats(db: Session = Depends(get_db)):
    return await DashboardService.get_quick_stats(db) 