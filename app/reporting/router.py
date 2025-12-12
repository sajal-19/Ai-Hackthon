# app/reporting/router.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_db, require_roles
from app.users_org.models import User, UserRole, Department
from app.trainings.models import Training
from app.enrollments_attendance.models import Enrollment, EnrollmentStatus

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get(
    "/departments/mandatory-completion",
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def department_mandatory_completion(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Mandatory trainings
    mandatory_training_ids = [
        t.id
        for t in db.query(Training.id).filter(Training.is_mandatory == True).all()
    ]

    # Employees per department
    # Note: assumes User has department_id
    dept_stats = (
        db.query(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            func.count(User.id).label("total_employees"),
        )
        .join(User, User.department_id == Department.id)
        .group_by(Department.id, Department.name)
        .all()
    )

    # Completed mandatory enrollments per department
    completed_stats = (
        db.query(
            Department.id.label("department_id"),
            func.count(func.distinct(Enrollment.user_id)).label("employees_completed_all"),
        )
        .join(User, User.department_id == Department.id)
        .join(Enrollment, Enrollment.user_id == User.id)
        .filter(
            Enrollment.training_id.in_(mandatory_training_ids),
            Enrollment.status == EnrollmentStatus.COMPLETED,
        )
        .group_by(Department.id)
        .all()
    )

    completed_map = {row.department_id: row.employees_completed_all for row in completed_stats}

    result = []
    for row in dept_stats:
        completed = completed_map.get(row.department_id, 0)
        result.append(
            {
                "department_id": row.department_id,
                "department_name": row.department_name,
                "total_employees": row.total_employees,
                "employees_completed_mandatory_any": completed,
            }
        )
    return result

@router.get(
    "/managers/mandatory-completion",
    dependencies=[Depends(require_roles(UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def manager_reportees_mandatory_completion(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.users_org.models import ManagerRelationship

    # reportees of this manager
    reportee_ids = [
        r.reportee_id
        for r in db.query(ManagerRelationship).filter(ManagerRelationship.manager_id == current_user.id).all()
    ]
    if not reportee_ids:
        return []

    mandatory_training_ids = [
        t.id
        for t in db.query(Training.id).filter(Training.is_mandatory == True).all()
    ]

    # completed mandatory per reportee
    completion_rows = (
        db.query(
            Enrollment.user_id,
            func.count(func.distinct(Enrollment.training_id)).label("completed_count"),
        )
        .filter(
            Enrollment.user_id.in_(reportee_ids),
            Enrollment.training_id.in_(mandatory_training_ids),
            Enrollment.status == EnrollmentStatus.COMPLETED,
        )
        .group_by(Enrollment.user_id)
        .all()
    )
    completion_map = {r.user_id: r.completed_count for r in completion_rows}

    # total mandatory trainings
    total_mandatory = len(mandatory_training_ids)

    users = db.query(User).filter(User.id.in_(reportee_ids)).all()

    result = []
    for u in users:
        completed = completion_map.get(u.id, 0)
        result.append(
            {
                "user_id": u.id,
                "name": u.full_name,
                "email": u.email,
                "completed_mandatory": completed,
                "total_mandatory": total_mandatory,
            }
        )

    return result
