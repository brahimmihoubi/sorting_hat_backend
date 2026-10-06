from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models import AdminUser, Answer, Department, Question, ScoringRule, Participant, SortingResult
from app.schemas.admin import AdminStatsResponse
from app.schemas.answer import AnswerAdminRead, AnswerCreate, AnswerUpdate
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.schemas.participant import ParticipantRead
from app.schemas.question import QuestionAdminRead, QuestionCreate, QuestionUpdate
from app.schemas.scoring_rule import ScoringRuleCreate, ScoringRuleRead, ScoringRuleUpdate
from app.schemas.sorting import SortResultResponse
from app.services.statistics_service import calculate_admin_statistics

router = APIRouter(prefix="/admin", tags=["Admin Dashboard & Management"])


# ====================================================
# STATISTICS & ANALYTICS
# ====================================================
@router.get("/statistics", response_model=AdminStatsResponse, summary="Get dashboard statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Retrieve real-time participant and department distribution statistics."""
    stats = calculate_admin_statistics(db)
    return stats


# ====================================================
# PARTICIPANTS & RESULTS LISTING
# ====================================================
@router.get("/participants", response_model=List[ParticipantRead], summary="List participants")
def list_participants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Retrieve paginated list of registered participants."""
    query = db.query(Participant)
    if status_filter:
        query = query.filter(Participant.status == status_filter)

    participants = query.order_by(Participant.created_at.desc()).offset(skip).limit(limit).all()
    return participants


@router.get("/results", response_model=List[SortResultResponse], summary="List all sorting results")
def list_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Retrieve paginated list of completed sorting results with score snapshots."""
    results = db.query(SortingResult).order_by(SortingResult.created_at.desc()).offset(skip).limit(limit).all()

    output = []
    for r in results:
        dept = db.query(Department).filter(Department.id == r.department_id).first()
        output.append(
            SortResultResponse(
                result_id=r.id,
                department={
                    "id": dept.id if dept else r.department_id,
                    "name": dept.name if dept else "Unknown",
                    "slug": dept.slug if dept else "unknown",
                    "icon": dept.icon if dept else None,
                    "color": dept.color if dept else None,
                },
                total_score=r.total_score,
                scores=r.scores_snapshot,
                scoring_version=r.scoring_version,
            )
        )
    return output


# ====================================================
# DEPARTMENT CRUD
# ====================================================
@router.get("/departments", response_model=List[DepartmentRead], summary="Admin list departments")
def admin_list_departments(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """List all departments (active and inactive) for admin management."""
    return db.query(Department).order_by(Department.display_order.asc()).all()


@router.post("/departments", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED, summary="Create department")
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Create a new department."""
    existing = db.query(Department).filter(Department.slug == dept_in.slug.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Department with slug '{dept_in.slug}' already exists.")

    dept = Department(**dept_in.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/departments/{dept_id}", response_model=DepartmentRead, summary="Update department")
def update_department(
    dept_id: str,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Update department details."""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")

    update_data = dept_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(dept, field, val)

    db.commit()
    db.refresh(dept)
    return dept


# ====================================================
# QUESTION CRUD
# ====================================================
@router.get("/questions", response_model=List[QuestionAdminRead], summary="Admin list questions")
def admin_list_questions(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """List all questions with complete answer lists for admin editing."""
    return db.query(Question).order_by(Question.display_order.asc()).all()


@router.post("/questions", response_model=QuestionAdminRead, status_code=status.HTTP_201_CREATED, summary="Create question")
def create_question(
    q_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Create a new questionnaire question."""
    q = Question(**q_in.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.put("/questions/{question_id}", response_model=QuestionAdminRead, summary="Update question")
def update_question(
    question_id: str,
    q_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Update question text or parameters."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    for field, val in q_in.model_dump(exclude_unset=True).items():
        setattr(q, field, val)

    db.commit()
    db.refresh(q)
    return q


# ====================================================
# ANSWER CRUD
# ====================================================
@router.post("/answers", response_model=AnswerAdminRead, status_code=status.HTTP_201_CREATED, summary="Create answer")
def create_answer(
    ans_in: AnswerCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Create an answer choice for a question."""
    q = db.query(Question).filter(Question.id == ans_in.question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    ans = Answer(**ans_in.model_dump())
    db.add(ans)
    db.commit()
    db.refresh(ans)
    return ans


@router.put("/answers/{answer_id}", response_model=AnswerAdminRead, summary="Update answer")
def update_answer(
    answer_id: str,
    ans_in: AnswerUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Update answer text or status."""
    ans = db.query(Answer).filter(Answer.id == answer_id).first()
    if not ans:
        raise HTTPException(status_code=404, detail="Answer not found.")

    for field, val in ans_in.model_dump(exclude_unset=True).items():
        setattr(ans, field, val)

    db.commit()
    db.refresh(ans)
    return ans


# ====================================================
# SCORING RULES CRUD
# ====================================================
@router.get("/scoring-rules", response_model=List[ScoringRuleRead], summary="Admin list scoring rules")
def admin_list_scoring_rules(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """List all scoring rules."""
    return db.query(ScoringRule).all()


@router.post("/scoring-rules", response_model=ScoringRuleRead, status_code=status.HTTP_201_CREATED, summary="Create scoring rule")
def create_scoring_rule(
    rule_in: ScoringRuleCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Create a new scoring rule."""
    rule = ScoringRule(**rule_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/scoring-rules/{rule_id}", response_model=ScoringRuleRead, summary="Update scoring rule")
def update_scoring_rule(
    rule_id: str,
    rule_in: ScoringRuleUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Update a scoring rule weight or trait."""
    rule = db.query(ScoringRule).filter(ScoringRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Scoring rule not found.")

    for field, val in rule_in.model_dump(exclude_unset=True).items():
        setattr(rule, field, val)

    db.commit()
    db.refresh(rule)
    return rule
