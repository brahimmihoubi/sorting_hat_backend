from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ScoringRuleBase(BaseModel):
    question_id: str
    answer_id: str
    department_id: Optional[str] = None
    weight: float = Field(0.0, ge=0.0)
    trait: Optional[str] = None
    trait_value: Optional[float] = None


class ScoringRuleCreate(ScoringRuleBase):
    pass


class ScoringRuleUpdate(BaseModel):
    department_id: Optional[str] = None
    weight: Optional[float] = None
    trait: Optional[str] = None
    trait_value: Optional[float] = None


class ScoringRuleRead(ScoringRuleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
