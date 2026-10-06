from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Department
from app.schemas.department import DepartmentRead

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentRead], summary="Get active departments")
def get_departments(db: Session = Depends(get_db)):
    """
    Retrieve list of active SDG departments ordered by display order.
    Publicly accessible endpoint for frontend house/department displays.
    """
    departments = (
        db.query(Department)
        .filter(Department.active == True)
        .order_by(Department.display_order.asc())
        .all()
    )
    return departments
