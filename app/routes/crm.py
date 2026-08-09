from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/crm", tags=["crm"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="crm")
def crm_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    contacts = db.query(Lead).order_by(Lead.id.desc()).all()
    return templates.TemplateResponse(
        "crm/index.html",
        {"request": request, "user": user, "contacts": contacts},
    )


@router.post("/update-status/{lead_id}")
def update_status(lead_id: int, request: Request, status_value: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        lead.status = status_value.strip() or "New"
        db.commit()

    return RedirectResponse(url="/crm", status_code=status.HTTP_303_SEE_OTHER)
