from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from schemas.anamnesis import Sex


class PatientCreateIn(BaseModel):
    date_of_birth: Optional[date] = None
    recorded_age: Optional[int] = None
    sex: Optional[Sex] = None


class PatientOut(BaseModel):
    id: int
    date_of_birth: Optional[date] = None
    recorded_age: Optional[int] = None
    sex: Optional[Sex] = None
    created_at: datetime
