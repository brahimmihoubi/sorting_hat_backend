from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.sorting import SortResultResponse, SortSubmitRequest
from app.services.sorting_service import (
    InvalidResponseSubmissionError,
    ParticipantAlreadySortedError,
    ParticipantNotFoundError,
    process_participant_sorting,
)

router = APIRouter(prefix="/sort", tags=["Sorting Engine"])


@router.post("", response_model=SortResultResponse, summary="Submit questionnaire & perform sorting")
def sort_participant(
    submit_in: SortSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit questionnaire responses for a participant and perform official department sorting.
    Calculates weighted department scores, applies leadership trait rules, resolves ties deterministically,
    and saves an immutable SortingResult score snapshot.
    """
    responses_tuples = [(r.question_id, r.answer_id) for r in submit_in.responses]

    try:
        result_data = process_participant_sorting(
            db=db,
            participant_id=submit_in.participant_id,
            responses_data=responses_tuples,
        )

        return SortResultResponse(
            result_id=result_data["result_id"],
            department=result_data["department"],
            total_score=result_data["total_score"],
            scores=result_data["scores"],
            scoring_version=result_data["scoring_version"],
        )

    except ParticipantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidResponseSubmissionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ParticipantAlreadySortedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during sorting calculation: {str(e)}",
        )
