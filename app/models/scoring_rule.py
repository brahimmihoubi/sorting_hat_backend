import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ScoringRule(Base):
    __tablename__ = "scoring_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_id = Column(String(36), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=True, index=True)
    weight = Column(Float, default=0.0, nullable=False)
    trait = Column(String(50), nullable=True)        # e.g., 'leadership'
    trait_value = Column(Float, nullable=True)       # e.g., 0.40, 0.70, 0.90
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    question = relationship("Question", back_populates="scoring_rules")
    answer = relationship("Answer", back_populates="scoring_rules")
    department = relationship("Department", back_populates="scoring_rules")
