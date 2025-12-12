# app/users_org/models.py
import enum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base

class UserRole(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    MANAGER = "MANAGER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(Enum(UserRole), nullable=False, index=True)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="users")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="department")

class ManagerRelationship(Base):
    __tablename__ = "manager_relationships"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reportee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    manager = relationship("User", foreign_keys=[manager_id], backref="reportees_rel")
    reportee = relationship("User", foreign_keys=[reportee_id], backref="manager_rel")

class OrgUnit(Base):
    __tablename__ = "org_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    parent_org_unit_id = Column(Integer, ForeignKey("org_units.id"), nullable=True)

    parent = relationship("OrgUnit", remote_side=[id], backref="children")
