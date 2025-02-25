from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.group_service import GroupService
from ..schemas.group import Group, GroupCreate, GroupDetail
from ..schemas.word import Word
from ..schemas.study_session import StudySession

router = APIRouter()

@router.get("/groups", response_model=List[Group])
async def get_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return await GroupService.get_groups(db, skip, limit)

@router.get("/groups/{group_id}", response_model=GroupDetail)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    group = await GroupService.get_group(db, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/groups/{group_id}/words", response_model=List[Word])
async def get_group_words(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    words = await GroupService.get_group_words(db, group_id, skip, limit)
    if words is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return words

@router.post("/groups", response_model=Group)
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    return await GroupService.create_group(db, group)

@router.get("/groups/{group_id}/study_sessions", response_model=List[StudySession])
async def get_group_study_sessions(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get all study sessions for a specific group"""
    try:
        sessions = await GroupService.get_group_study_sessions(db, group_id)
        if sessions is None:
            raise HTTPException(status_code=404, detail="Group not found")
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 