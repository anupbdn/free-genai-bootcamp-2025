from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.study_session_service import StudySessionService
from ..schemas.study_session import StudySession, StudySessionCreate, StudySessionDetail

router = APIRouter()

@router.get("/study_sessions", response_model=List[StudySession])
async def get_study_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return await StudySessionService.get_study_sessions(db, skip, limit)

@router.get("/study_sessions/{session_id}", response_model=StudySessionDetail)
async def get_study_session(session_id: int, db: Session = Depends(get_db)):
    session = await StudySessionService.get_study_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Study session not found")
    return session

@router.post("/study_sessions", response_model=StudySession)
async def create_study_session(
    session: StudySessionCreate,
    db: Session = Depends(get_db)
):
    return await StudySessionService.create_study_session(db, session) 