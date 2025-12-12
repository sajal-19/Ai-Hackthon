# app/trainings/schemas.py
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from app.trainings.models import (
    TrainingMode,
    AssignmentTargetType,
    TrainingApprovalStatus,
)


class TrainingBase(BaseModel):
    title: str
    description: Optional[str] = None
    department_id: Optional[int] = None
    duration_hours: int = 1
    mode: TrainingMode = TrainingMode.ONLINE
    is_mandatory: bool = False


class TrainingCreate(TrainingBase):
    pass


class TrainingRead(TrainingBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainingAssignmentBase(BaseModel):
    target_type: AssignmentTargetType
    target_department_id: Optional[int] = None
    target_user_id: Optional[int] = None


class TrainingAssignmentCreate(TrainingAssignmentBase):
    training_id: int


class TrainingAssignmentRead(TrainingAssignmentBase):
    id: int
    training_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingApprovalRead(BaseModel):
    id: int
    training_id: int
    requested_by_id: int
    approved_by_id: Optional[int] = None
    status: TrainingApprovalStatus
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
