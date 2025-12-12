# app/auth/router.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.auth.deps import get_db
from app.core.config import get_settings
from app.users_org import models

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        role=user.role.value,
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
