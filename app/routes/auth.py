import os
import secrets
from hashlib import pbkdf2_hmac
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models import User

router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="app/templates")


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    derived_key = pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 390_000)
    return f"pbkdf2_sha256$390000${salt}${derived_key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        _, iterations, salt, hash_hex = stored_hash.split("$")
        iterations = int(iterations)
        derived_key = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return derived_key.hex() == hash_hex
    except (ValueError, AttributeError):
        return False


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Load the currently authenticated user from the session."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.get("/login", name="login")
@router.get("/auth/login", include_in_schema=False) 
def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@router.post("/login")
@router.post("/auth/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Invalid email or password."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register", name="register")
@router.get("/auth/register", include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse(request, "auth/register.html", {"error": None})


@router.post("/register")
@router.post("/auth/register")
def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    normalized_email = email.lower().strip()
    if not full_name.strip() or not normalized_email or not password:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {"error": "Please provide your full name, email, and a password."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {"error": "An account with that email already exists."},
            status_code=status.HTTP_409_CONFLICT,
        )

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
