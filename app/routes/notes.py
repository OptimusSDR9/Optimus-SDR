from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead, Note
from app.routes.auth import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="notes")
def notes_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    return templates.TemplateResponse(
        "notes/index.html",
        {"request": request, "user": user, "leads": leads, "notes": []},
    )


@router.get("/{lead_id}", name="lead_notes")
def lead_notes_page(lead_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return RedirectResponse(url="/notes", status_code=status.HTTP_303_SEE_OTHER)

    notes = db.query(Note).filter(Note.lead_id == lead_id).order_by(Note.id.desc()).all()
    return templates.TemplateResponse(
        "notes/index.html",
        {"request": request, "user": user, "leads": db.query(Lead).order_by(Lead.id.desc()).all(), "selected_lead": lead, "notes": notes},
    )


@router.post("/{lead_id}")
def add_note(
    lead_id: int,
    request: Request,
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return RedirectResponse(url="/notes", status_code=status.HTTP_303_SEE_OTHER)

    note = Note(lead_id=lead_id, content=content.strip(), created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(note)
    db.commit()

    return RedirectResponse(url=f"/notes/{lead_id}", status_code=status.HTTP_303_SEE_OTHER)
