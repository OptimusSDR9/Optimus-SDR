from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/leads", tags=["leads"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="leads")
def list_leads(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    return templates.TemplateResponse(
        request,
        "leads/list.html",
        {"user": user, "leads": leads},
    )


@router.get("/new", name="new_lead")
def new_lead_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "leads/form.html", {"user": user, "lead": None})


@router.post("/new")
def create_lead(
    request: Request,
    practice_name: str = Form(...),
    doctor_name: str = Form(...),
    specialty: str = Form(default=""),
    website: str = Form(default=""),
    email: str = Form(default=""),
    phone: str = Form(default=""),
    state: str = Form(default=""),
    status: str = Form(default="New"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    lead = Lead(
        practice_name=practice_name.strip(),
        doctor_name=doctor_name.strip(),
        specialty=specialty.strip(),
        website=website.strip(),
        email=email.strip(),
        phone=phone.strip(),
        state=state.strip(),
        status=status.strip() or "New",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return RedirectResponse(url="/leads", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{lead_id}/edit", name="edit_lead")
def edit_lead_page(lead_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return RedirectResponse(url="/leads", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request,
        "leads/form.html",
        {"user": user, "lead": lead},
    )


@router.post("/{lead_id}/edit")
def update_lead(
    lead_id: int,
    request: Request,
    practice_name: str = Form(...),
    doctor_name: str = Form(...),
    specialty: str = Form(default=""),
    website: str = Form(default=""),
    email: str = Form(default=""),
    phone: str = Form(default=""),
    state: str = Form(default=""),
    status: str = Form(default="New"),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return RedirectResponse(url="/leads", status_code=status.HTTP_303_SEE_OTHER)

    lead.practice_name = practice_name.strip()
    lead.doctor_name = doctor_name.strip()
    lead.specialty = specialty.strip()
    lead.website = website.strip()
    lead.email = email.strip()
    lead.phone = phone.strip()
    lead.state = state.strip()
    lead.status = status.strip() or "New"

    db.commit()
    return RedirectResponse(url="/leads", status_code=status.HTTP_303_SEE_OTHER)
