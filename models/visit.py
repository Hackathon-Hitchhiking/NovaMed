from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.BaseModel import EntityMeta
from .anamnesis import Anamnesis
from .visit_examination import VisitExamination
from .diagnosis_suggestion import DiagnosisSuggestion
from .referral_suggestion import ReferralSuggestion
from .diagnosis import Diagnosis


class Visit(EntityMeta):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True
    )
    doctor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="in_progress")

    patient: Mapped["Patient"] = relationship(back_populates="visits")
    anamnesis: Mapped[Optional["Anamnesis"]] = relationship(
        back_populates="visit", uselist=False, cascade="all, delete-orphan"
    )
    exam_results: Mapped[List["VisitExamination"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )
    suggestions: Mapped[List["DiagnosisSuggestion"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )
    referrals: Mapped[List["ReferralSuggestion"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )
    diagnoses: Mapped[List["Diagnosis"]] = relationship(
        back_populates="visit", cascade="all, delete-orphan"
    )
