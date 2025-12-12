# app/certificates/schemas.py
from datetime import datetime
from pydantic import BaseModel


class CertificateRead(BaseModel):
    id: int
    user_id: int
    badge_id: int
    template_type: str
    issued_at: datetime
    metadata: str | None = None

    class Config:
        from_attributes = True
