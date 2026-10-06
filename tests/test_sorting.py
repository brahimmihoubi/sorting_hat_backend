import uuid
import pytest
from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.models import Department, Participant, Question, Answer
from app.seed.seed_data import seed_db
from app.services.sorting_service import (
    process_participant_sorting,
    ParticipantNotFoundError,
    InvalidResponseSubmissionError,
)


@pytest.fixture(scope="module")
def db_session():
    """Module-level database session fixture for testing sorting service."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_db(db)
    yield db
    db.close()


def test_pure_development_sorting(db_session: Session):
    """Test that picking option A for all questions assigns participant to Development."""
    token = f"dev_token_{uuid.uuid4().hex}"
    participant = Participant(
        full_name="Dev Test User",
        email=f"dev_{uuid.uuid4().hex[:6]}@example.com",
        academic_year="Master 1",
        session_token=token,
        status="started",
    )
    db_session.add(participant)
    db_session.commit()

    questions = db_session.query(Question).filter(Question.active == True).order_by(Question.display_order).all()

    responses = []
    for q in questions:
        ans_a = db_session.query(Answer).filter(Answer.question_id == q.id, Answer.display_order == 1).first()
        responses.append((q.id, ans_a.id))

    result = process_participant_sorting(db_session, participant.id, responses)

    assert result["department"]["slug"] == "development"
    assert result["scores"]["development"] > result["scores"]["design"]
    assert result["already_completed"] is False

    # Idempotency re-submission check
    result2 = process_participant_sorting(db_session, participant.id, responses)
    assert result2["result_id"] == result["result_id"]
    assert result2["department"]["slug"] == "development"


def test_pure_design_sorting(db_session: Session):
    """Test that picking option B for all questions assigns participant to Design."""
    token = f"design_token_{uuid.uuid4().hex}"
    participant = Participant(
        full_name="Design Test User",
        email=f"design_{uuid.uuid4().hex[:6]}@example.com",
        academic_year="Licence 3",
        session_token=token,
        status="started",
    )
    db_session.add(participant)
    db_session.commit()

    questions = db_session.query(Question).filter(Question.active == True).order_by(Question.display_order).all()

    responses = []
    for q in questions:
        ans_b = db_session.query(Answer).filter(Answer.question_id == q.id, Answer.display_order == 2).first()
        responses.append((q.id, ans_b.id))

    result = process_participant_sorting(db_session, participant.id, responses)

    assert result["department"]["slug"] == "design"
    assert result["scores"]["design"] > result["scores"]["events"]


def test_missing_question_validation(db_session: Session):
    """Test that missing responses raises InvalidResponseSubmissionError."""
    token = f"inc_token_{uuid.uuid4().hex}"
    participant = Participant(
        full_name="Incomplete User",
        email=f"inc_{uuid.uuid4().hex[:6]}@example.com",
        academic_year="Licence 1",
        session_token=token,
        status="started",
    )
    db_session.add(participant)
    db_session.commit()

    questions = db_session.query(Question).filter(Question.active == True).order_by(Question.display_order).all()

    ans_a = db_session.query(Answer).filter(Answer.question_id == questions[0].id).first()
    incomplete_responses = [(questions[0].id, ans_a.id)]

    with pytest.raises(InvalidResponseSubmissionError):
        process_participant_sorting(db_session, participant.id, incomplete_responses)
