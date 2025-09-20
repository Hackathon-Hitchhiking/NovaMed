from typing import Optional

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.BaseModel import EntityMeta
from models.enums import ModalityEnum


class Examination(EntityMeta):
    __tablename__ = "examinations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    modality: Mapped[str] = mapped_column(ModalityEnum, default="other", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
