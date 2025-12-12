# app/profiles/router.py
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_db, require_roles
from app.users_org.models import User, UserRole
from app.enrollments_attendance.models import Enrollment, EnrollmentStatus
from app.trainings.models import Training
from app.profiles import models, schemas

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _get_or_create_profile(db: Session, user_id: int) -> models.LearningProfile:
    profile = (
        db.query(models.LearningProfile)
        .filter(models.LearningProfile.user_id == user_id)
        .first()
    )
    if not profile:
        profile = models.LearningProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/me", response_model=schemas.LearningProfileRead)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = _get_or_create_profile(db, current_user.id)

    certs = (
        db.query(models.Certification)
        .filter(models.Certification.user_id == current_user.id)
        .all()
    )
    history = (
        db.query(models.TrainingHistoryEntry)
        .filter(models.TrainingHistoryEntry.user_id == current_user.id)
        .all()
    )

    # Manual assembly into Pydantic schema
    return schemas.LearningProfileRead(
        user_id=current_user.id,
        tech_stack=profile.tech_stack,
        total_learning_hours_current_year=profile.total_learning_hours_current_year,
        certifications=certs,
        training_history=history,
    )


@router.patch("/me", response_model=schemas.LearningProfileRead)
def update_my_profile(
    update_in: schemas.LearningProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = _get_or_create_profile(db, current_user.id)

    if update_in.tech_stack is not None:
        profile.tech_stack = update_in.tech_stack

    db.commit()
    db.refresh(profile)

    certs = (
        db.query(models.Certification)
        .filter(models.Certification.user_id == current_user.id)
        .all()
    )
    history = (
        db.query(models.TrainingHistoryEntry)
        .filter(models.TrainingHistoryEntry.user_id == current_user.id)
        .all()
    )

    return schemas.LearningProfileRead(
        user_id=current_user.id,
        tech_stack=profile.tech_stack,
        total_learning_hours_current_year=profile.total_learning_hours_current_year,
        certifications=certs,
        training_history=history,
    )


@router.post(
    "/me/certifications",
    response_model=schemas.CertificationRead,
    status_code=status.HTTP_201_CREATED,
)
def add_my_certification(
    cert_in: schemas.CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = models.Certification(
        user_id=current_user.id,
        name=cert_in.name,
        issuer=cert_in.issuer,
        issue_date=cert_in.issue_date,
        expiry_date=cert_in.expiry_date,
        linked_training_id=cert_in.linked_training_id,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert

@router.get(
    "/users/{user_id}",
    response_model=schemas.LearningProfileRead,
    dependencies=[Depends(require_roles(UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def get_user_profile_for_manager(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Managers can only see their reportees; Admin/Super Admin can see anyone
    if current_user.role == UserRole.MANAGER:
        from app.users_org.models import ManagerRelationship
        rel = (
            db.query(ManagerRelationship)
            .filter(
                ManagerRelationship.manager_id == current_user.id,
                ManagerRelationship.reportee_id == user_id,
            )
            .first()
        )
        if not rel:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this user's profile",
            )

    profile = _get_or_create_profile(db, user_id)

    certs = (
        db.query(models.Certification)
        .filter(models.Certification.user_id == user_id)
        .all()
    )
    history = (
        db.query(models.TrainingHistoryEntry)
        .filter(models.TrainingHistoryEntry.user_id == user_id)
        .all()
    )

    return schemas.LearningProfileRead(
        user_id=user_id,
        tech_stack=profile.tech_stack,
        total_learning_hours_current_year=profile.total_learning_hours_current_year,
        certifications=certs,
        training_history=history,
    )
