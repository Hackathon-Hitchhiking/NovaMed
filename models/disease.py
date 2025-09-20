from typing import Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from models.BaseModel import EntityMeta


class Disease(EntityMeta):
    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
