import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Participant
from app.schemas.participant import ParticipantCreate, ParticipantRead

router = APIRouter(prefix="/participants", tags=["Participants"])


@router.post("", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED, summary="Register participant session")
def create_participant(
    participant_in: ParticipantCreate,
    db: Session = Depends(get_db),
):
    """
    Register a participant session prior to questionnaire completion.
    Generates a unique session_token used for sorting validation.
    """
    # Generate unique session token
    session_token = f"sdg_session_{uuid.uuid4().hex}"

    participant = Participant(
        full_name=participant_in.full_name.strip(),
        email=participant_in.email.strip().lower(),
        academic_year=participant_in.academic_year.strip(),
        session_token=session_token,
        status="started",
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant
