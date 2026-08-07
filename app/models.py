from sqlalchemy import Column, Integer, String

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    practice_name = Column(String(255))
    doctor_name = Column(String(255))
    specialty = Column(String(100))
    website = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    state = Column(String(100))
    status = Column(String(50), default="New")