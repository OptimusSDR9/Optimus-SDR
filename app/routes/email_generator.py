from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/email-generator", tags=["email-generator"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="email_generator")
def email_generator_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    return templates.TemplateResponse(
        "email_generator/index.html",
        {"request": request, "user": user, "leads": leads, "draft": None},
    )


@router.post("")
def generate_email(
    request: Request,
    lead_id: int = Form(...),
    tone: str = Form(default="professional"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    leads = db.query(Lead).order_by(Lead.id.desc()).all()

    if not lead:
        return templates.TemplateResponse(
            "email_generator/index.html",
            {"request": request, "user": user, "leads": leads, "draft": None, "error": "Lead not found."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    draft = build_email_draft(lead, tone)
    return templates.TemplateResponse(
        "email_generator/index.html",
        {"request": request, "user": user, "leads": leads, "draft": draft, "selected_id": lead.id},
    )


def build_email_draft(lead: Lead, tone: str) -> str:
    specialty = lead.specialty or "your specialty"
    practice_name = lead.practice_name or "your practice"
    opening = {
        "professional": "Hello",
        "friendly": "Hi",
        "direct": "Hello",
    }.get(tone, "Hello")

    subject = f"Helping {practice_name} improve revenue operations"
    body = (
        f"{opening} {lead.doctor_name or 'there'},\n\n"
        f"I work with healthcare practices like {practice_name} to improve revenue cycle visibility and reduce administrative friction. "
        f"Your {specialty.lower()} practice appears to be a strong fit for a conversation about how better workflow automation can support growth.\n\n"
        f"If you are open to it, I would be happy to share a brief overview of how we support providers in your space.\n\n"
        "Best regards,\n"
        "Optimus AI SDR"
    )

    return f"Subject: {subject}\n\n{body}"
