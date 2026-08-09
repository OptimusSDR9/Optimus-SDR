import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config.database import Base, engine
from app.database import initialize_database
from app.models import Lead, Note, User
from app.routes import auth, dashboard, leads
from app.routes.leads_api import router as leads_api_router

initialize_database()

app = FastAPI(title="Optimus AI SDR", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "optimus-sdr-dev-secret"))
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(leads.router)
app.include_router(leads_api_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Optimus AI SDR"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})
