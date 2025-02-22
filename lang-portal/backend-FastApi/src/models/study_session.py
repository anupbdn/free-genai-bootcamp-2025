from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    study_activity_id = Column(Integer, ForeignKey("study_activities.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    group = relationship("Group", backref="study_sessions")
    activity = relationship("StudyActivity", back_populates="sessions")
    review_items = relationship("WordReviewItem", back_populates="study_session") 