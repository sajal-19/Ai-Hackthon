# app/certificates/router.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_db
from app.users_org.models import User
from app.certificates import models, schemas

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/me", response_model=List[schemas.CertificateRead])
def list_my_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    certs = (
        db.query(models.Certificate)
        .filter(models.Certificate.user_id == current_user.id)
        .all()
    )
    return certs
