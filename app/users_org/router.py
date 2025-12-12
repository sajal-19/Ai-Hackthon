# app/users_org/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from . import models, schemas


router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # TODO: replace with proper password hashing and admin auth check
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=user_in.password,  # placeholder
        role=user_in.role,
        department_id=user_in.department_id,
        is_active=user_in.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    # TODO: restrict to Admin/Super Admin
    return db.query(models.User).all()
