from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100, example="Development")
    slug: str = Field(..., max_length=50, example="development")
    description: Optional[str] = Field(None, example="Technical thinking, problem solving, building, technology")
    short_description: Optional[str] = Field(None, example="Building digital solutions and solving complex problems")
    icon: Optional[str] = Field(None, example="code")
    color: Optional[str] = Field(None, example="#3B82F6")
    active: bool = True
    display_order: int = 0


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None
    display_order: Optional[int] = None


class DepartmentRead(DepartmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentSimple(BaseModel):
    id: str
    name: str
    slug: str
    icon: Optional[str] = None
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
