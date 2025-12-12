# app/users_org/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.users_org import models, schemas
from app.auth.security import hash_password
from app.auth.deps import get_current_user, require_roles

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(models.UserRole.ADMIN, models.UserRole.SUPER_ADMIN))],
)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=hash_password(user_in.password),
        role=user_in.role,
        department_id=user_in.department_id,
        is_active=user_in.is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get(
    "",
    response_model=List[schemas.UserRead],
    dependencies=[Depends(require_roles(models.UserRole.ADMIN, models.UserRole.SUPER_ADMIN))],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.User).all()
