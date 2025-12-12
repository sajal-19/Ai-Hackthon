# app/certificates/models.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)

    template_type = Column(String, nullable=False)  # e.g., SILVER/GOLD/PLATINUM
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    metadata = Column(Text, nullable=True)  # placeholder for template data, link, etc.

    user = relationship("User")
    badge = relationship("Badge")
