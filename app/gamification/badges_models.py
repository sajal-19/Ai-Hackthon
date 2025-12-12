# app/gamification/badges_models.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # SILVER/GOLD/PLATINUM
    threshold_hours = Column(Integer, nullable=False)  # 25/50/100

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)

    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    badge = relationship("Badge")
    user = relationship("User")
