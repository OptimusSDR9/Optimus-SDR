import os
import secrets

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine, get_db, initialize_database
from app.routes.analytics import router as analytics_router
from app.routes.analyzer import router as analyzer_router
from app.routes.auth import get_current_user, router as auth_router
from app.routes.crm import router as crm_router
from app.routes.dashboard import router as dashboard_router
from app.routes.email_generator import router as email_generator_router
from app.routes.followup import router as followup_router
from app.routes.leads import router as leads_router
from app.routes.leads_api import router as leads_api_router
from app.routes.notes import router as notes_router
from app.routes.reply_detection import router as reply_detection_router
from app.routes.scoring import router as scoring_router
from app.routes.settings import router as settings_router
from app.routes.zoho_mail import router as zoho_mail_router
import app.models

app = FastAPI(
    title="Optimus AI SDR",
    version="1.0.0",
    description="AI Sales Development Representative for Optimus RCM Solutions",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY") or secrets.token_urlsafe(32),
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(leads_router)
app.include_router(leads_api_router)
app.include_router(crm_router)
app.include_router(analyzer_router)
app.include_router(scoring_router)
app.include_router(email_generator_router)
app.include_router(zoho_mail_router)
app.include_router(followup_router)
app.include_router(reply_detection_router)
app.include_router(notes_router)
app.include_router(analytics_router)
app.include_router(settings_router)

initialize_database()

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("home.html", {"request": request})
