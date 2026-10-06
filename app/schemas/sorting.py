from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.department import DepartmentSimple


class SingleResponseSubmit(BaseModel):
    question_id: str = Field(..., description="UUID of the question answered")
    answer_id: str = Field(..., description="UUID of the selected answer")


class SortSubmitRequest(BaseModel):
    participant_id: str = Field(..., description="UUID of the participant submitting questionnaire")
    responses: List[SingleResponseSubmit] = Field(..., min_length=1, description="List of responses for all required questions")


class SortResultResponse(BaseModel):
    result_id: str = Field(..., description="UUID of the created sorting result")
    department: DepartmentSimple = Field(..., description="Assigned department details")
    total_score: float = Field(..., description="Highest score achieved by the winning department")
    scores: Dict[str, float] = Field(..., description="Complete breakdown of scores for all departments")
    scoring_version: str = Field("v1.0", description="Version of the scoring engine used")

    model_config = ConfigDict(from_attributes=True)
