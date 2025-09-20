from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.BaseModel import EntityMeta


class VisitExamination(EntityMeta):
    __tablename__ = "visit_examinations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id", ondelete="CASCADE"), index=True
    )
    # store examination name directly instead of FK
    examination_name: Mapped[str] = mapped_column(String(128), nullable=False)

    result_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    s3_path: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    visit: Mapped["Visit"] = relationship(back_populates="exam_results")
