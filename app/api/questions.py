from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models import Answer, Question
from app.schemas.question import QuestionPublicRead

router = APIRouter(prefix="/questions", tags=["Questionnaire"])


@router.get("", response_model=List[QuestionPublicRead], summary="Get questionnaire questions & answers")
def get_questions(db: Session = Depends(get_db)):
    """
    Retrieve active questionnaire questions and their answer choices.
    Hidden classification categories and scoring weights are strictly excluded from response.
    """
    questions = (
        db.query(Question)
        .filter(Question.active == True)
        .order_by(Question.display_order.asc())
        .all()
    )

    # Filter active answers per question ordered by display_order
    for q in questions:
        q.answers = [a for a in q.answers if a.active]
        q.answers.sort(key=lambda x: x.display_order)

    return questions
