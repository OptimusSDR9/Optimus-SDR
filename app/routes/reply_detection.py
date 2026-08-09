from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.routes.auth import get_current_user

router = APIRouter(prefix="/reply-detection", tags=["reply-detection"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="reply_detection")
def reply_detection_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    leads = db.query(Lead).order_by(Lead.id.desc()).all()
    return templates.TemplateResponse(
        "reply_detection/index.html",
        {"request": request, "user": user, "leads": leads, "result": None},
    )


@router.post("")
def detect_reply(
    request: Request,
    lead_id: int = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    leads = db.query(Lead).order_by(Lead.id.desc()).all()

    if not lead:
        return templates.TemplateResponse(
            "reply_detection/index.html",
            {"request": request, "user": user, "leads": leads, "result": {"success": False, "message": "Lead not found."}},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    result = classify_reply(message)
    return templates.TemplateResponse(
        "reply_detection/index.html",
        {"request": request, "user": user, "leads": leads, "result": {"lead": lead, **result}, "selected_id": lead.id},
    )


def classify_reply(message: str) -> dict:
    text = (message or "").strip().lower()

    positive_keywords = {"yes", "interested", "love", "sounds good", "great", "happy", "sure", "definitely", "open"}
    negative_keywords = {"no", "not interested", "busy", "not now", "unsubscribe", "stop", "no thanks"}

    if any(keyword in text for keyword in negative_keywords):
        sentiment = "negative"
        action = "pause outreach and log a low-priority follow-up"
    elif any(keyword in text for keyword in positive_keywords):
        sentiment = "positive"
        action = "advance to a meeting or proposal step"
    else:
        sentiment = "neutral"
        action = "continue the standard follow-up cadence"

    return {"sentiment": sentiment, "action": action}
