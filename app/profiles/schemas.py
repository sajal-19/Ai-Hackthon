# app/profiles/schemas.py
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel


class CertificationBase(BaseModel):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    linked_training_id: Optional[int] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationRead(CertificationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingHistoryEntryRead(BaseModel):
    id: int
    user_id: int
    training_id: int
    status: str
    completion_date: Optional[date] = None
    hours_credited: int
    created_at: datetime

    class Config:
        from_attributes = True


class LearningProfileBase(BaseModel):
    tech_stack: Optional[str] = None  # can store JSON string or comma-separated tags


class LearningProfileUpdate(LearningProfileBase):
    pass


class LearningProfileRead(LearningProfileBase):
    user_id: int
    total_learning_hours_current_year: int
    certifications: List[CertificationRead] = []
    training_history: List[TrainingHistoryEntryRead] = []

    class Config:
        from_attributes = True
