from pathlib import Path
import textwrap

root = Path(r"c:\Users\Ajey\Downloads\Optimus-AI-SDR")
files = {
    "app/config/__init__.py": "",
    "app/config/database.py": '''from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./optimus_sdr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
    "app/models/__init__.py": "from .user import User\nfrom .lead import Lead\n",
    "app/models/user.py": '''from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
''',
    "app/models/lead.py": '''from datetime import datetime
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
    status = Column(String, default="New")
    tags = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
''',
    "app/schemas/__init__.py": "",
    "app/schemas/user.py": '''from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
''',
    "app/schemas/lead.py": '''from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeadCreate(BaseModel):
    practice_name: str
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    npi: Optional[str] = None


class LeadResponse(LeadCreate):
    id: int
    lead_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
''',
    "app/auth/__init__.py": "",
    "app/auth/security.py": '''from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "optimus-rcm-super-secret-key-production-2026"
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
''',
    "app/routes/__init__.py": "from .auth import router as auth\nfrom .dashboard import router as dashboard\nfrom .leads import router as leads\n",
    "app/routes/auth.py": '''from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.config.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/register", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/api/auth/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_pwd, full_name=user_in.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
''',
    "app/routes/dashboard.py": '''from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", include_in_schema=False)
def dashboard_page(request: Request):
    stats = {"total_leads": 124, "qualified_leads": 42, "emails_sent": 85, "replies_received": 18}
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})
''',
    "app/routes/leads.py": '''from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/leads", include_in_schema=False)
def leads_page(request: Request, db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return templates.TemplateResponse("leads/list.html", {"request": request, "leads": leads})


@router.post("/api/leads", response_model=LeadResponse)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    new_lead = Lead(**lead_in.dict())
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead
''',
}

for rel_path, content in files.items():
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

print("repair script completed")
