from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/followup", tags=["followup"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="followup")
def followup_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    queue = []
    for lead in leads:
        queue.append(build_followup_plan(lead))

    return templates.TemplateResponse(
        "followup/index.html",
        {"request": request, "user": user, "queue": queue},
    )


@router.post("/schedule")
def schedule_followup(request: Request, lead_id: int = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        lead.status = "Follow-up Scheduled"
        db.commit()

    return RedirectResponse(url="/followup", status_code=status.HTTP_303_SEE_OTHER)


def build_followup_plan(lead: Lead) -> dict:
    start_date = datetime.utcnow().date()
    steps = [
        {"label": "Initial outreach", "due": start_date + timedelta(days=0)},
        {"label": "Follow-up 1", "due": start_date + timedelta(days=5)},
        {"label": "Follow-up 2", "due": start_date + timedelta(days=12)},
        {"label": "Close / nurture", "due": start_date + timedelta(days=26)},
    ]

    return {
        "lead": lead,
        "steps": steps,
        "status": lead.status,
    }
