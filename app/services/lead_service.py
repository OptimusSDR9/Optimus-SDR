from datetime import datetime
from math import ceil
from typing import Optional

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query, Session

from app.models import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


SORTABLE_FIELDS = {
    "id": Lead.id,
    "practice_name": Lead.practice_name,
    "doctor_name": Lead.doctor_name,
    "specialty": Lead.specialty,
    "state": Lead.state,
    "status": Lead.status,
    "priority": Lead.priority,
    "lead_score": Lead.lead_score,
    "created_at": Lead.created_at,
    "updated_at": Lead.updated_at,
}


def _clean_values(values: dict) -> dict:
    return {
        key: value.strip() if isinstance(value, str) else value
        for key, value in values.items()
    }


def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
    lead = Lead(**_clean_values(lead_data.model_dump()))
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead(db: Session, lead: Lead, lead_data: LeadUpdate) -> Lead:
    values = _clean_values(lead_data.model_dump(exclude_unset=True))
    for field, value in values.items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead: Lead) -> None:
    db.delete(lead)
    db.commit()


def _filtered_query(
    db: Session,
    *,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    specialty: Optional[str] = None,
) -> Query:
    query = db.query(Lead)
    if search:
        search_value = f"%{search.strip()}%"
        query = query.filter(
            Lead.practice_name.ilike(search_value)
            | Lead.doctor_name.ilike(search_value)
            | Lead.email.ilike(search_value)
            | Lead.phone.ilike(search_value)
        )
    if status:
        query = query.filter(Lead.status.ilike(status.strip()))
    if priority:
        query = query.filter(Lead.priority.ilike(priority.strip()))
    if specialty:
        query = query.filter(Lead.specialty.ilike(f"%{specialty.strip()}%"))
    return query


def list_leads(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    specialty: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Lead], int, int]:
    query = _filtered_query(
        db,
        search=search,
        status=status,
        priority=priority,
        specialty=specialty,
    )
    total = query.count()
    sort_column = SORTABLE_FIELDS.get(sort_by, Lead.created_at)
    query = query.order_by(
        (asc(sort_column) if sort_order.lower() == "asc" else desc(sort_column)),
        desc(Lead.id),
    )
    leads = query.offset((page - 1) * page_size).limit(page_size).all()
    pages = ceil(total / page_size) if total else 0
    return leads, total, pages
