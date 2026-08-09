import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/zoho-mail", tags=["zoho-mail"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="zoho_mail")
def zoho_mail_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    return templates.TemplateResponse(
        "zoho_mail/index.html",
        {"request": request, "user": user, "leads": leads, "result": None},
    )


@router.post("")
def send_email(
    request: Request,
    lead_id: int = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    leads = db.query(Lead).order_by(Lead.id.desc()).all()

    if not lead:
        return templates.TemplateResponse(
            "zoho_mail/index.html",
            {"request": request, "user": user, "leads": leads, "result": {"success": False, "message": "Lead not found."}},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    result = dispatch_via_zoho(lead, subject, body)
    return templates.TemplateResponse(
        "zoho_mail/index.html",
        {"request": request, "user": user, "leads": leads, "result": result, "selected_id": lead.id},
    )


def dispatch_via_zoho(lead: Lead, subject: str, body: str) -> dict:
    api_key = os.getenv("ZOHO_API_KEY")
    sender = os.getenv("ZOHO_FROM_EMAIL")

    if not api_key or not sender:
        return {
            "success": False,
            "message": "Zoho Mail configuration is incomplete. Set ZOHO_API_KEY and ZOHO_FROM_EMAIL in your environment.",
        }

    payload = {
        "from": sender,
        "to": lead.email or "",
        "subject": subject,
        "body": body,
    }

    try:
        response = httpx.post(
            "https://api.zoho.com/mail/send",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return {"success": False, "message": "Zoho Mail request failed. Verify your credentials and endpoint configuration."}

    return {"success": True, "message": "Email dispatched successfully via Zoho Mail."}
