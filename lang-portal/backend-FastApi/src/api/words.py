from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.word_service import WordService
from ..schemas.word import Word, WordCreate, WordUpdate, WordWithStats

router = APIRouter()

@router.get("/words", response_model=List[Word])
async def get_words(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    words = await WordService.get_words(db, skip, limit)
    return words

@router.get("/words/{word_id}", response_model=WordWithStats)
async def get_word(word_id: int, db: Session = Depends(get_db)):
    word = await WordService.get_word(db, word_id)
    if word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return word

@router.post("/words", response_model=Word)
async def create_word(word: WordCreate, db: Session = Depends(get_db)):
    return await WordService.create_word(db, word)

@router.put("/words/{word_id}", response_model=Word)
async def update_word(
    word_id: int,
    word: WordUpdate,
    db: Session = Depends(get_db)
):
    updated_word = await WordService.update_word(db, word_id, word)
    if updated_word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return updated_word 