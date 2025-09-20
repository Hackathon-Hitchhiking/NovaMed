from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VisitCreateIn(BaseModel):
    patient_id: int
    doctor_id: Optional[str] = None


class VisitCreateOut(BaseModel):
    visit_id: int


class VisitOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: Optional[str] = None
    status: str
    created_at: datetime
