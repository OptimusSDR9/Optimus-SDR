from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(500), nullable=False)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    practice_name = Column(String(255), nullable=False)
    doctor_name = Column(String(255), nullable=False)
    specialty = Column(String(100))
    website = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    state = Column(String(100))
    status = Column(String(50), default="New")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(String(50), nullable=False)