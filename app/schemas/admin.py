from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.department import DepartmentRead
from app.schemas.participant import ParticipantRead


class AdminLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="admin@sdg.dz")
    password: str = Field(..., min_length=6, example="admin123")


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str
    admin_email: str


class AdminUserRead(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentDistribution(BaseModel):
    development: int = 0
    design: int = 0
    events: int = 0
    social_media: int = 0


class DepartmentPercentages(BaseModel):
    development: float = 0.0
    design: float = 0.0
    events: float = 0.0
    social_media: float = 0.0


class AdminStatsResponse(BaseModel):
    total_participants: int
    completed_sortings: int
    completion_rate_percentage: float
    department_distribution: DepartmentDistribution
    department_percentages: DepartmentPercentages
    total_interests_submitted: int
