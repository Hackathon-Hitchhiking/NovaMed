from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.BaseModel import EntityMeta


class Diagnosis(EntityMeta):
    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id", ondelete="CASCADE"), index=True
    )
    disease_id: Mapped[int] = mapped_column(
        ForeignKey("diseases.id", ondelete="RESTRICT"), index=True
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    visit: Mapped["Visit"] = relationship(back_populates="diagnoses")
    disease: Mapped["Disease"] = relationship()
