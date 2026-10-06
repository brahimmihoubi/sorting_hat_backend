import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class DepartmentInterest(Base):
    __tablename__ = "department_interests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    result_id = Column(String(36), ForeignKey("sorting_results.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False, index=True)
    interested = Column(Boolean, default=True, nullable=False)
    message = Column(Text, nullable=True)
    contact_preference = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    result = relationship("SortingResult", back_populates="interests")
    participant = relationship("Participant", back_populates="interests")
    department = relationship("Department", back_populates="interests")
