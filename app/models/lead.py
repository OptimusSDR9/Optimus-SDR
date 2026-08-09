from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.config.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    practice_name = Column(String, index=True, nullable=False)
    doctor_name = Column(String, nullable=True)
    specialty = Column(String, index=True, nullable=True)
    state = Column(String, nullable=True)
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    npi = Column(String, unique=True, index=True, nullable=True)
    insurance = Column(String, nullable=True)
    decision_maker = Column(String, nullable=True)
    lead_score = Column(Float, default=0.0)
    status = Column(String, default="New", index=True, nullable=False)
    priority = Column(String(50), default="Medium", index=True, nullable=False)
    tags = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
