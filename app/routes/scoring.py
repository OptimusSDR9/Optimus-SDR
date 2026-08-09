from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/scoring", tags=["scoring"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="scoring")
def scoring_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    scored_leads = []
    for lead in leads:
        score, reasons = calculate_score(lead)
        scored_leads.append({"lead": lead, "score": score, "reasons": reasons})

    return templates.TemplateResponse(
        "scoring/index.html",
        {"request": request, "user": user, "scored_leads": scored_leads},
    )


def calculate_score(lead: Lead) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    healthcare_specialties = {
        "psychiatry",
        "radiology",
        "behavioral health",
        "pain management",
        "family medicine",
        "primary care",
        "neurology",
        "dermatology",
        "orthopedics",
        "urology",
    }

    if lead.specialty:
        specialty_text = lead.specialty.lower()
        if specialty_text in healthcare_specialties:
            score += 30
            reasons.append("Specialty aligns with the target healthcare vertical.")
        else:
            score += 10
            reasons.append("Specialty is present but not yet matched to a known priority segment.")
    else:
        reasons.append("Specialty information is missing.")

    if lead.state:
        score += 10
        reasons.append("Location data is available.")
    else:
        reasons.append("State is missing.")

    if lead.website:
        score += 15
        reasons.append("Website information is present.")
    else:
        reasons.append("Website is missing.")

    if lead.email and lead.phone:
        score += 20
        reasons.append("Contact details are complete.")
    elif lead.email or lead.phone:
        score += 10
        reasons.append("Partial contact information is available.")
    else:
        reasons.append("Contact details are missing.")

    if lead.status in {"Qualified", "Meeting Scheduled", "Proposal Sent"}:
        score += 15
        reasons.append("Lead is already progressing through the funnel.")
    elif lead.status == "New":
        reasons.append("Lead is still in the initial stage.")

    score = max(0, min(100, score))
    return score, reasons
