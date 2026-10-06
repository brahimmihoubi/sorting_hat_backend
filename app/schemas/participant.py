from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ParticipantCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    academic_year: str = Field(..., min_length=1, max_length=100, example="Master 1")


class ParticipantRead(BaseModel):
    id: str
    full_name: str
    email: str
    academic_year: str
    session_token: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
