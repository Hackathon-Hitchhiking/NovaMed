from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class DiagnosisSuggestionOut(BaseModel):
    disease_name: str
    probability: float
    rationale: Optional[str] = None


class ReferralSuggestionOut(BaseModel):
    specialty: str
    note: Optional[str] = None


class PredictionsOut(BaseModel):
    suggestions: List[DiagnosisSuggestionOut]
    referrals: List[ReferralSuggestionOut]


class PredictionsWithArtifactsOut(PredictionsOut):
    s3_path: str
    visit_examination_id: int
