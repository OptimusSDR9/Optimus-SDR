import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models import Lead, Note
from app.routes.auth import get_current_user
from app.utils.onboarding import build_onboarding_steps

router = APIRouter(tags=["dashboard"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    total_leads = db.query(Lead).count()
    new_leads = db.query(Lead).filter(Lead.status == "New").count()
    qualified_leads = db.query(Lead).filter(Lead.status.in_(["Qualified", "Meeting Scheduled", "Proposal Sent"])).count()
    recent_leads = db.query(Lead).order_by(Lead.id.desc()).limit(5).all()
    total_notes = db.query(Note).count()
    onboarding = build_onboarding_steps(
        total_leads=total_leads,
        total_notes=total_notes,
        settings_configured=bool((os.getenv("OPENAI_API_KEY") or "").strip() and (os.getenv("ZOHO_API_KEY") or "").strip()),
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "total_leads": total_leads,
            "new_leads": new_leads,
            "qualified_leads": qualified_leads,
            "recent_leads": recent_leads,
            "onboarding": onboarding,
        },
    )
