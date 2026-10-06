from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# Public answer schema (hides all scoring rules / categories)
class AnswerPublicRead(BaseModel):
    id: str
    text: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class AnswerBase(BaseModel):
    text: str = Field(..., min_length=1)
    display_order: int = 0
    active: bool = True


class AnswerCreate(AnswerBase):
    question_id: str


class AnswerUpdate(BaseModel):
    text: Optional[str] = None
    display_order: Optional[int] = None
    active: Optional[bool] = None


class AnswerAdminRead(AnswerBase):
    id: str
    question_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
