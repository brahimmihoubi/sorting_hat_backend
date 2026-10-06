from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.answer import AnswerAdminRead, AnswerPublicRead


# Public question schema (hides scoring logic)
class QuestionPublicRead(BaseModel):
    id: str
    text: str
    type: str
    display_order: int
    required: bool
    answers: List[AnswerPublicRead] = []

    model_config = ConfigDict(from_attributes=True)


class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1)
    type: str = "single_choice"
    display_order: int = 0
    required: bool = True
    active: bool = True


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[str] = None
    display_order: Optional[int] = None
    required: Optional[bool] = None
    active: Optional[bool] = None


class QuestionAdminRead(QuestionBase):
    id: str
    answers: List[AnswerAdminRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
