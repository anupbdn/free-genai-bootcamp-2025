from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..core.database import Base

# Association table for many-to-many relationship between words and groups
words_groups = Table(
    'words_groups',
    Base.metadata,
    Column('word_id', Integer, ForeignKey('words.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    japanese = Column(String, index=True, nullable=False)
    romaji = Column(String, nullable=False)
    english = Column(String, nullable=False)
    parts = Column(JSON)

    # Relationships
    groups = relationship("Group", secondary=words_groups, back_populates="words")
    # Move this relationship to WordReviewItem model instead
    # review_items = relationship("WordReviewItem", back_populates="word")

    def __repr__(self):
        return f"<Word {self.japanese}>" 