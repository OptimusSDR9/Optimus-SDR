from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models import User
from app.routes.auth import require_current_user
from app.schemas.lead import LeadCreate, LeadListResponse, LeadResponse, LeadUpdate
from app.services.lead_service import (
    create_lead,
    delete_lead,
    get_lead,
    list_leads,
    update_lead,
)


router = APIRouter(prefix="/api/leads", tags=["lead-management"])


def _get_lead_or_404(db: Session, lead_id: int):
    lead = get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


def _list_response(
    db: Session,
    *,
    page: int,
    page_size: int,
    search: Optional[str],
    status_filter: Optional[str],
    priority_filter: Optional[str],
    specialty_filter: Optional[str],
    sort_by: str,
    sort_order: str,
) -> LeadListResponse:
    leads, total, pages = list_leads(
        db,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        priority=priority_filter,
        specialty=specialty_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return LeadListResponse(
        items=leads,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead_endpoint(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_current_user),
):
    return create_lead(db, lead_data)


@router.get("", response_model=LeadListResponse)
def list_leads_endpoint(
    search: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority_filter: Optional[str] = Query(default=None, alias="priority"),
    specialty_filter: Optional[str] = Query(default=None, alias="specialty"),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="(?i)^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_current_user),
):
    return _list_response(
        db,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        priority_filter=priority_filter,
        specialty_filter=specialty_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/search", response_model=LeadListResponse)
def search_leads_endpoint(
    search: str = Query(min_length=1),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority_filter: Optional[str] = Query(default=None, alias="priority"),
    specialty_filter: Optional[str] = Query(default=None, alias="specialty"),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="(?i)^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_current_user),
):
    return _list_response(
        db,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        priority_filter=priority_filter,
        specialty_filter=specialty_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_current_user),
):
    return _get_lead_or_404(db, lead_id)


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead_endpoint(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_current_user),
):
    lead = _get_lead_or_404(db, lead_id)
    return update_lead(db, lead, lead_data)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead_endpoint(
    lead_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_current_user),
):
    lead = _get_lead_or_404(db, lead_id)
    delete_lead(db, lead)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
