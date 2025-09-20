from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.BaseModel import EntityMeta
from .disease import Disease


class DiagnosisSuggestion(EntityMeta):
    __tablename__ = "diagnosis_suggestions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id", ondelete="CASCADE"), index=True
    )
    disease_id: Mapped[int] = mapped_column(
        ForeignKey("diseases.id", ondelete="RESTRICT"), index=True
    )
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    visit: Mapped["Visit"] = relationship(back_populates="suggestions")
    disease: Mapped["Disease"] = relationship()

    __table_args__ = (
        UniqueConstraint("visit_id", "disease_id", name="uq_suggestion_visit_disease"),
        Index("ix_suggestion_prob_desc", "probability"),
    )
