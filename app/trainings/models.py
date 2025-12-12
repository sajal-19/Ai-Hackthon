# app/trainings/models.py
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.users_org.models import Department, User  # for type hints only


class TrainingMode(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    HYBRID = "HYBRID"


class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    duration_hours = Column(Integer, nullable=False, default=1)
    mode = Column(Enum(TrainingMode), nullable=False, default=TrainingMode.ONLINE)

    is_mandatory = Column(Boolean, nullable=False, default=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    department = relationship("Department")
    created_by = relationship("User")


class AssignmentTargetType(str, enum.Enum):
    ALL = "ALL"
    DEPARTMENT = "DEPARTMENT"
    USER = "USER"


class TrainingAssignment(Base):
    __tablename__ = "training_assignments"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=False)

    target_type = Column(Enum(AssignmentTargetType), nullable=False)
    target_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    training = relationship("Training")
    target_department = relationship("Department")
    target_user = relationship("User")


class TrainingApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TrainingApproval(Base):
    __tablename__ = "training_approvals"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("trainings.id"), unique=True, nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(Enum(TrainingApprovalStatus), nullable=False, default=TrainingApprovalStatus.PENDING)
    comments = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    training = relationship("Training", foreign_keys=[training_id])
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
