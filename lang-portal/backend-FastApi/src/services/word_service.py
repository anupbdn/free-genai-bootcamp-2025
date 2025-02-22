from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.word import Word
from ..schemas.word import WordCreate, WordUpdate

class WordService:
    @staticmethod
    async def get_words(db: Session, skip: int = 0, limit: int = 100) -> List[Word]:
        return db.query(Word).offset(skip).limit(limit).all()

    @staticmethod
    async def get_word(db: Session, word_id: int) -> Optional[Word]:
        return db.query(Word).filter(Word.id == word_id).first()

    @staticmethod
    async def create_word(db: Session, word: WordCreate) -> Word:
        db_word = Word(**word.dict())
        db.add(db_word)
        db.commit()
        db.refresh(db_word)
        return db_word

    @staticmethod
    async def update_word(db: Session, word_id: int, word: WordUpdate) -> Optional[Word]:
        db_word = await WordService.get_word(db, word_id)
        if db_word:
            for key, value in word.dict(exclude_unset=True).items():
                setattr(db_word, key, value)
            db.commit()
            db.refresh(db_word)
        return db_word 