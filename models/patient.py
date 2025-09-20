from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.BaseModel import EntityMeta
from models.enums import SexEnum
from .visit import Visit


class Patient(EntityMeta):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # DOB optional; can store recorded age instead
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    recorded_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(SexEnum, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    visits: Mapped[List["Visit"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
