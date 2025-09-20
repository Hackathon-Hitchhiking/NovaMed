from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Sex(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class General(BaseModel):
    age: Optional[int] = None
    sex: Optional[Sex] = None


class Genetic(BaseModel):
    has_family_history: Optional[bool] = None
    details: Optional[str] = None


class Smoking(BaseModel):
    yes: Optional[bool] = None
    years: Optional[int] = None


class Lifestyle(BaseModel):
    smoking: Optional[Smoking] = None
    alcohol: Optional[str] = None
    activity: Optional[str] = None
    diet: Optional[List[str]] = None


class AnamnesisIn(BaseModel):
    general: Optional[General] = None
    genetic: Optional[Genetic] = None
    lifestyle: Optional[Lifestyle] = None
    past_conditions: Optional[List[str]] = None
    surgeries_traumas: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    complaints: Optional[List[str]] = None


class AnamnesisUpsertOut(BaseModel):
    anamnesis_id: int
