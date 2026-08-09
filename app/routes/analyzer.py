import re
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.auth import get_current_user

router = APIRouter(prefix="/analyzer", tags=["analyzer"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", name="analyzer")
def analyzer_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("analyzer/index.html", {"request": request, "user": user, "result": None})


@router.post("")
def analyze_website(
    request: Request,
    website_url: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)

    cleaned_url = normalize_url(website_url)
    if not cleaned_url:
        return templates.TemplateResponse(
            "analyzer/index.html",
            {"request": request, "user": user, "result": {"error": "Please provide a valid website URL."}},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    result = scrape_site(cleaned_url)
    return templates.TemplateResponse(
        "analyzer/index.html",
        {"request": request, "user": user, "result": result},
    )


def normalize_url(url: str) -> Optional[str]:
    value = (url or "").strip()
    if not value:
        return None
    if not re.match(r"^https?://", value):
        value = f"https://{value}"
    return value


def scrape_site(url: str) -> dict:
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError:
        return {"error": "Unable to fetch the website. Please verify the URL and try again."}

    text = response.text
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    title = clean_text(title_match.group(1)) if title_match else "Untitled page"

    description_match = re.search(r"<meta[^>]+name=['\"]description['\"][^>]+content=['\"](.*?)['\"]", text, re.IGNORECASE | re.DOTALL)
    description = clean_text(description_match.group(1)) if description_match else "No meta description found."

    headings = re.findall(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    heading_text = clean_text(" ".join(headings[:3])) if headings else "No H1 heading found."

    body_text = re.sub(r"<script.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    body_text = re.sub(r"<style.*?</style>", " ", body_text, flags=re.IGNORECASE | re.DOTALL)
    body_text = re.sub(r"<[^>]+>", " ", body_text)
    body_text = re.sub(r"\s+", " ", body_text)
    body_text = clean_text(body_text[:1800])

    insight = generate_insight(title, description, heading_text, body_text)

    return {
        "url": url,
        "title": title,
        "description": description,
        "heading": heading_text,
        "body_preview": body_text,
        "insight": insight,
    }


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def generate_insight(title: str, description: str, heading: str, body: str) -> str:
    hints = []
    if "health" in title.lower() or "health" in description.lower() or "health" in body.lower():
        hints.append("Healthcare-focused positioning is visible.")
    if "care" in title.lower() or "care" in description.lower() or "care" in body.lower():
        hints.append("Patient care and service language are prominent.")
    if "clinic" in title.lower() or "clinic" in description.lower() or "clinic" in body.lower():
        hints.append("Clinic or practice operations are emphasized.")
    if not hints:
        hints.append("The site appears to be a general business website with limited healthcare-specific signals.")
    return " ".join(hints)
