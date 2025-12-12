# app/enrollments_attendance/schemas.py
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel

from app.enrollments_attendance.models import EnrollmentStatus


class EnrollmentBase(BaseModel):
    training_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentRead(EnrollmentBase):
    id: int
    user_id: int
    status: EnrollmentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttendanceRecordBase(BaseModel):
    enrollment_id: int
    session_date: date
    attended: bool = True


class AttendanceRecordCreate(AttendanceRecordBase):
    pass


class AttendanceRecordRead(AttendanceRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
