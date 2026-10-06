import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Department, Participant, Question, Response, ScoringRule, SortingResult

logger = logging.getLogger("sdg_sorting_hat.sorting_service")


class SortingServiceError(Exception):
    """Base exception for sorting service errors."""

    pass


class ParticipantNotFoundError(SortingServiceError):
    """Raised when participant ID is not found."""

    pass


class ParticipantAlreadySortedError(SortingServiceError):
    """Raised when participant has already completed sorting."""

    pass


class InvalidResponseSubmissionError(SortingServiceError):
    """Raised when questionnaire responses fail validation."""

    pass


def process_participant_sorting(
    db: Session,
    participant_id: str,
    responses_data: List[Tuple[str, str]],  # List of (question_id, answer_id) tuples
) -> Dict[str, Any]:
    """
    Pure business logic function to validate responses, compute department scores,
    resolve ties deterministically, and persist immutable SortingResult.
    """

    # 1. Fetch & validate participant
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise ParticipantNotFoundError(f"Participant with ID {participant_id} not found.")

    # Idempotency check: if participant already completed sorting, return existing result
    existing_result = db.query(SortingResult).filter(SortingResult.participant_id == participant_id).first()
    if existing_result:
        winning_dept = db.query(Department).filter(Department.id == existing_result.department_id).first()
        return {
            "result_id": existing_result.id,
            "department": {
                "id": winning_dept.id if winning_dept else existing_result.department_id,
                "name": winning_dept.name if winning_dept else "Unknown",
                "slug": winning_dept.slug if winning_dept else "unknown",
                "icon": winning_dept.icon if winning_dept else None,
                "color": winning_dept.color if winning_dept else None,
            },
            "total_score": existing_result.total_score,
            "scores": existing_result.scores_snapshot,
            "scoring_version": existing_result.scoring_version,
            "already_completed": True,
        }

    # 2. Validate active questions & submitted responses
    active_questions = db.query(Question).filter(Question.active == True, Question.required == True).all()
    active_question_ids = {q.id for q in active_questions}

    submitted_q_ids = {q_id for q_id, _ in responses_data}

    # Verify duplicate question answers in submission
    if len(submitted_q_ids) != len(responses_data):
        raise InvalidResponseSubmissionError("Duplicate responses submitted for the same question.")

    # Verify all required active questions are answered
    missing_q_ids = active_question_ids - submitted_q_ids
    if missing_q_ids:
        raise InvalidResponseSubmissionError(f"Missing responses for {len(missing_q_ids)} required question(s).")

    # 3. Load active departments & initialize score dict
    active_departments = (
        db.query(Department)
        .filter(Department.active == True)
        .order_by(Department.display_order)
        .all()
    )
    if not active_departments:
        raise SortingServiceError("No active departments available for sorting.")

    dept_by_id = {d.id: d for d in active_departments}
    dept_by_slug = {d.slug: d for d in active_departments}
    scores: Dict[str, float] = {d.slug: 0.0 for d in active_departments}

    # 4. Save participant responses & accumulate weighted scores
    for q_id, a_id in responses_data:
        # Save response record
        resp = Response(
            participant_id=participant_id,
            question_id=q_id,
            answer_id=a_id,
        )
        db.add(resp)

        # Query scoring rules for this (question_id, answer_id)
        rules = (
            db.query(ScoringRule)
            .filter(ScoringRule.question_id == q_id, ScoringRule.answer_id == a_id)
            .all()
        )

        for rule in rules:
            if rule.department_id and rule.department_id in dept_by_id:
                target_slug = dept_by_id[rule.department_id].slug
                if target_slug in scores:
                    scores[target_slug] += float(rule.weight)

    # Round scores for clean presentation
    scores = {slug: round(sc, 2) for slug, sc in scores.items()}

    # 5. Deterministic Tie-Breaking Logic
    max_score = max(scores.values())
    top_slugs = [slug for slug, sc in scores.items() if sc == max_score]

    if len(top_slugs) == 1:
        winning_slug = top_slugs[0]
    else:
        # Tie-Breaker Step 1: Sum scores from primary department-specific questions (Q1, Q5, Q8)
        primary_q_ids = set(
            q_id
            for (q_id,) in db.query(Question.id)
            .filter(Question.display_order.in_([1, 5, 8]))
            .all()
        )

        primary_scores = {slug: 0.0 for slug in top_slugs}
        for q_id, a_id in responses_data:
            if q_id in primary_q_ids:
                rules = (
                    db.query(ScoringRule)
                    .filter(ScoringRule.question_id == q_id, ScoringRule.answer_id == a_id)
                    .all()
                )
                for rule in rules:
                    if rule.department_id and rule.department_id in dept_by_id:
                        d_slug = dept_by_id[rule.department_id].slug
                        if d_slug in primary_scores:
                            primary_scores[d_slug] += float(rule.weight)

        max_primary = max(primary_scores.values())
        primary_winners = [slug for slug, sc in primary_scores.items() if sc == max_primary]

        if len(primary_winners) == 1:
            winning_slug = primary_winners[0]
        else:
            # Tie-Breaker Step 2: Use deterministic department display_order
            winning_slug = sorted(
                primary_winners,
                key=lambda s: dept_by_slug[s].display_order,
            )[0]

    winning_dept = dept_by_slug[winning_slug]

    # 6. Create immutable SortingResult
    result = SortingResult(
        participant_id=participant_id,
        department_id=winning_dept.id,
        total_score=max_score,
        scores_snapshot=scores,
        scoring_version=settings.SCORING_VERSION,
    )
    db.add(result)

    # 7. Update participant completion status
    participant.status = "completed"
    participant.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(result)

    logger.info(f"Sorted participant {participant.full_name} -> {winning_dept.name} (Score: {max_score})")

    return {
        "result_id": result.id,
        "department": {
            "id": winning_dept.id,
            "name": winning_dept.name,
            "slug": winning_dept.slug,
            "icon": winning_dept.icon,
            "color": winning_dept.color,
        },
        "total_score": max_score,
        "scores": scores,
        "scoring_version": result.scoring_version,
        "already_completed": False,
    }
