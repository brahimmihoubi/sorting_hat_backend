from typing import Any, Dict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Department, DepartmentInterest, Participant, SortingResult


def calculate_admin_statistics(db: Session) -> Dict[str, Any]:
    """
    Calculate real-time dashboard statistics from database queries.
    """
    total_participants = db.query(Participant).count()
    completed_sortings = db.query(SortingResult).count()

    completion_rate = (
        round((completed_sortings / total_participants) * 100, 2)
        if total_participants > 0
        else 0.0
    )

    # Base department distribution counter
    distribution = {
        "development": 0,
        "design": 0,
        "events": 0,
        "social_media": 0,
    }

    # Execute DB count grouped by department slug
    results = (
        db.query(Department.slug, func.count(SortingResult.id))
        .join(SortingResult, Department.id == SortingResult.department_id)
        .group_by(Department.slug)
        .all()
    )

    for slug, count in results:
        if slug in distribution:
            distribution[slug] = count

    percentages = {}
    for slug, count in distribution.items():
        pct = round((count / completed_sortings) * 100, 2) if completed_sortings > 0 else 0.0
        percentages[slug] = pct

    total_interests = db.query(DepartmentInterest).count()

    return {
        "total_participants": total_participants,
        "completed_sortings": completed_sortings,
        "completion_rate_percentage": completion_rate,
        "department_distribution": distribution,
        "department_percentages": percentages,
        "total_interests_submitted": total_interests,
    }
