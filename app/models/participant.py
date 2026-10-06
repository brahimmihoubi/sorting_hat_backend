import uuid
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    academic_year = Column(String(100), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(30), default="started", nullable=False)  # 'started', 'completed'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    responses = relationship("Response", back_populates="participant", cascade="all, delete-orphan")
    result = relationship("SortingResult", back_populates="participant", uselist=False, cascade="all, delete-orphan")
    interests = relationship("DepartmentInterest", back_populates="participant", cascade="all, delete-orphan")
