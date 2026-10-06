import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SortingResult(Base):
    __tablename__ = "sorting_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False, index=True)
    total_score = Column(Float, nullable=False)
    scores_snapshot = Column(JSON, nullable=False)  # Stores {"development": 87, "design": 61, ...}
    scoring_version = Column(String(30), nullable=False, default="v1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    participant = relationship("Participant", back_populates="result")
    department = relationship("Department", back_populates="results")
    interests = relationship("DepartmentInterest", back_populates="result", cascade="all, delete-orphan")
