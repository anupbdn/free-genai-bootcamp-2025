from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
from .word import words_groups

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    words = relationship("Word", secondary=words_groups, back_populates="groups")
    # Remove this line and move to StudySession model
    # study_sessions = relationship("StudySession", back_populates="group") 