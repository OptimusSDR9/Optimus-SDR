from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead, Note
from app.routes.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="analytics")
def analytics_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).all()
    note_count = db.query(Note).count()

    by_status = {}
    for lead in leads:
        by_status[lead.status or "New"] = by_status.get(lead.status or "New", 0) + 1

    summary = {
        "total_leads": len(leads),
        "qualified": sum(1 for lead in leads if lead.status in {"Qualified", "Meeting Scheduled", "Proposal Sent", "Follow-up Scheduled"}),
        "new": sum(1 for lead in leads if lead.status == "New"),
        "notes": note_count,
        "by_status": by_status,
    }

    return templates.TemplateResponse(
        "analytics/index.html",
        {"request": request, "user": user, "summary": summary},
    )
