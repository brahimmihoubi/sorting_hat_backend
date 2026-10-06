from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InterestCreate(BaseModel):
    interested: bool = Field(True, description="Whether participant is interested in joining")
    message: Optional[str] = Field(None, max_length=1000, description="Optional message or note")
    contact_preference: Optional[str] = Field(None, max_length=50, description="Preferred contact method (Email, Discord, Phone)")


class InterestRead(InterestCreate):
    id: str
    result_id: str
    participant_id: str
    department_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
