# app/enrollments_attendance/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_db, require_roles
from app.users_org.models import User, UserRole
from app.trainings.models import Training
from app.enrollments_attendance import models, schemas

from datetime import date
from app.profiles.models import LearningProfile, TrainingHistoryEntry

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post(
    "",
    response_model=schemas.EnrollmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_enrollment(
    enrollment_in: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training = db.query(Training).filter(Training.id == enrollment_in.training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    existing = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.training_id == enrollment_in.training_id,
            models.Enrollment.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled",
        )

    enrollment = models.Enrollment(
        training_id=enrollment_in.training_id,
        user_id=current_user.id,
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get(
    "",
    response_model=List[schemas.EnrollmentRead],
    dependencies=[Depends(get_current_user)],
)
def list_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == current_user.id)
        .all()
    )


@router.post(
    "/{enrollment_id}/complete",
    response_model=schemas.EnrollmentRead,
    dependencies=[Depends(get_current_user)],
)
def mark_enrollment_completed(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.id == enrollment_id,
            models.Enrollment.user_id == current_user.id,
        )
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    training = db.query(Training).filter(Training.id == enrollment.training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    # Mark enrollment as completed
    enrollment.status = models.EnrollmentStatus.COMPLETED
    db.commit()
    db.refresh(enrollment)

    # Update training history
    today = date.today()
    history_entry = TrainingHistoryEntry(
        user_id=current_user.id,
        training_id=training.id,
        status="COMPLETED",
        completion_date=today,
        hours_credited=training.duration_hours,
    )
    db.add(history_entry)

    # Update learning profile and yearly hours
    profile = (
        db.query(LearningProfile)
        .filter(LearningProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        profile = LearningProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()

    if today.year == today.year:  # current year
        profile.total_learning_hours_current_year += training.duration_hours

    db.commit()
    return enrollment


@router.post(
    "/attendance",
    response_model=schemas.AttendanceRecordRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MANAGER))],
)
def create_attendance_record(
    record_in: schemas.AttendanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.id == record_in.enrollment_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    record = models.AttendanceRecord(
        enrollment_id=record_in.enrollment_id,
        session_date=record_in.session_date,
        attended=record_in.attended,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record
