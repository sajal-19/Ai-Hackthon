# app/trainings/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles, get_db
from app.users_org.models import User, UserRole
from app.trainings import models, schemas

from app.enrollments_attendance.models import Enrollment, EnrollmentStatus

router = APIRouter(prefix="/trainings", tags=["trainings"])


@router.post(
    "",
    response_model=schemas.TrainingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def create_training(
    training_in: schemas.TrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training = models.Training(
        title=training_in.title,
        description=training_in.description,
        department_id=training_in.department_id,
        duration_hours=training_in.duration_hours,
        mode=training_in.mode,
        is_mandatory=training_in.is_mandatory,
        created_by_id=current_user.id,
    )

    db.add(training)
    db.commit()
    db.refresh(training)

    # For mandatory trainings, create a pending approval request
    if training.is_mandatory:
        approval = models.TrainingApproval(
            training_id=training.id,
            requested_by_id=current_user.id,
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)

    return training


@router.get(
    "",
    response_model=List[schemas.TrainingRead],
    dependencies=[Depends(get_current_user)],
)
def list_trainings(
    db: Session = Depends(get_db),
):
    return db.query(models.Training).all()


@router.post(
    "/assignments",
    response_model=schemas.TrainingAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def create_training_assignment(
    assignment_in: schemas.TrainingAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training = db.query(models.Training).filter(models.Training.id == assignment_in.training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    # Basic validation: ensure target fields align with target_type
    if assignment_in.target_type == models.AssignmentTargetType.ALL:
        if assignment_in.target_department_id or assignment_in.target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ALL assignments must not specify department or user",
            )
    elif assignment_in.target_type == models.AssignmentTargetType.DEPARTMENT:
        if not assignment_in.target_department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DEPARTMENT assignments require target_department_id",
            )
    elif assignment_in.target_type == models.AssignmentTargetType.USER:
        if not assignment_in.target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="USER assignments require target_user_id",
            )

    assignment = models.TrainingAssignment(
        training_id=assignment_in.training_id,
        target_type=assignment_in.target_type,
        target_department_id=assignment_in.target_department_id,
        target_user_id=assignment_in.target_user_id,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get(
    "/assignments",
    response_model=List[schemas.TrainingAssignmentRead],
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def list_training_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(models.TrainingAssignment).all()

@router.get(
    "/mandatory/status",
    dependencies=[Depends(get_current_user)],
)
def get_my_mandatory_training_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Trainings marked mandatory
    mandatory_trainings = db.query(models.Training).filter(models.Training.is_mandatory == True).all()

    # Enrollments for current user
    enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id)
        .all()
    )
    enrollment_by_training = {e.training_id: e for e in enrollments}

    result = []
    for t in mandatory_trainings:
        enrollment = enrollment_by_training.get(t.id)
        status = "NOT_ENROLLED"
        if enrollment:
            if enrollment.status == EnrollmentStatus.COMPLETED:
                status = "COMPLETED"
            else:
                status = "IN_PROGRESS"
        result.append(
            {
                "training_id": t.id,
                "title": t.title,
                "status": status,
            }
        )
    return result
