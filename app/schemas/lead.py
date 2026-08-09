from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeadBase(BaseModel):
    practice_name: str = Field(min_length=1, max_length=255)
    doctor_name: Optional[str] = Field(default=None, max_length=255)
    specialty: Optional[str] = Field(default=None, max_length=255)
    state: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=500)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    linkedin: Optional[str] = Field(default=None, max_length=500)
    npi: Optional[str] = Field(default=None, max_length=50)
    insurance: Optional[str] = Field(default=None, max_length=255)
    decision_maker: Optional[str] = Field(default=None, max_length=255)
    lead_score: float = Field(default=0.0, ge=0.0)
    status: str = Field(default="New", min_length=1, max_length=50)
    priority: str = Field(default="Medium", min_length=1, max_length=50)
    tags: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    practice_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    doctor_name: Optional[str] = Field(default=None, max_length=255)
    specialty: Optional[str] = Field(default=None, max_length=255)
    state: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=500)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    linkedin: Optional[str] = Field(default=None, max_length=500)
    npi: Optional[str] = Field(default=None, max_length=50)
    insurance: Optional[str] = Field(default=None, max_length=255)
    decision_maker: Optional[str] = Field(default=None, max_length=255)
    lead_score: Optional[float] = Field(default=None, ge=0.0)
    status: Optional[str] = Field(default=None, min_length=1, max_length=50)
    priority: Optional[str] = Field(default=None, min_length=1, max_length=50)
    tags: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    pages: int
