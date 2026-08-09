import os

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="settings")
def settings_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY") or "",
        "zoho_api_key": os.getenv("ZOHO_API_KEY") or "",
        "zoho_from_email": os.getenv("ZOHO_FROM_EMAIL") or "",
        "session_secret_key": os.getenv("SESSION_SECRET_KEY") or "",
    }

    return templates.TemplateResponse(
        "settings/index.html",
        {"request": request, "user": user, "config": config, "saved": False},
    )


@router.post("")
def save_settings(
    request: Request,
    openai_api_key: str = Form(default=""),
    zoho_api_key: str = Form(default=""),
    zoho_from_email: str = Form(default=""),
    session_secret_key: str = Form(default=""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    # In a production deployment, these values would be persisted securely.
    # This implementation keeps them in environment variables for safety.
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if zoho_api_key:
        os.environ["ZOHO_API_KEY"] = zoho_api_key
    if zoho_from_email:
        os.environ["ZOHO_FROM_EMAIL"] = zoho_from_email
    if session_secret_key:
        os.environ["SESSION_SECRET_KEY"] = session_secret_key

    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY") or "",
        "zoho_api_key": os.getenv("ZOHO_API_KEY") or "",
        "zoho_from_email": os.getenv("ZOHO_FROM_EMAIL") or "",
        "session_secret_key": os.getenv("SESSION_SECRET_KEY") or "",
    }

    return templates.TemplateResponse(
        "settings/index.html",
        {"request": request, "user": user, "config": config, "saved": True},
    )
