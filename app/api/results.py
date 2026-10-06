from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Department, DepartmentInterest, SortingResult
from app.schemas.interest import InterestCreate
from app.schemas.sorting import SortResultResponse

router = APIRouter(prefix="/results", tags=["Sorting Results"])


@router.get("/{result_id}", response_model=SortResultResponse, summary="Get sorting result by ID")
def get_sorting_result(
    result_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve completed sorting result by result ID.
    Returns assigned department info, total score, breakdown scores snapshot, and scoring version.
    """
    result = db.query(SortingResult).filter(SortingResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sorting result with ID '{result_id}' not found.",
        )

    dept = db.query(Department).filter(Department.id == result.department_id).first()

    return SortResultResponse(
        result_id=result.id,
        department={
            "id": dept.id if dept else result.department_id,
            "name": dept.name if dept else "Unknown",
            "slug": dept.slug if dept else "unknown",
            "icon": dept.icon if dept else None,
            "color": dept.color if dept else None,
        },
        total_score=result.total_score,
        scores=result.scores_snapshot,
        scoring_version=result.scoring_version,
    )


@router.post("/{result_id}/interest", summary="Express interest in joining assigned department")
def record_department_interest(
    result_id: str,
    interest_in: InterestCreate,
    db: Session = Depends(get_db),
):
    """
    Allow participant to submit interest or contact request for their sorted department.
    """
    result = db.query(SortingResult).filter(SortingResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sorting result with ID '{result_id}' not found.",
        )

    interest = DepartmentInterest(
        result_id=result.id,
        participant_id=result.participant_id,
        department_id=result.department_id,
        interested=interest_in.interested,
        message=interest_in.message.strip() if interest_in.message else None,
        contact_preference=interest_in.contact_preference.strip() if interest_in.contact_preference else None,
    )
    db.add(interest)
    db.commit()
    db.refresh(interest)

    return {
        "status": "success",
        "message": "Interest request recorded successfully.",
        "interest_id": interest.id,
    }
