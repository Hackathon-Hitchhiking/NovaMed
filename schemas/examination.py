from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ExamResultData(BaseModel):
    class Config:
        extra = "allow"


class ExamUploadIn(BaseModel):
    examination_name: str
    content: bytes
    filename: Optional[str] = None
    content_type: Optional[str] = None
    result_text: Optional[str] = None
    result_data: Optional[ExamResultData] = None


class ExamUploadOut(BaseModel):
    s3_path: str
    visit_examination_id: int


class ExamResultOut(BaseModel):
    id: int
    examination_name: str
    s3_path: str
    result_text: Optional[str] = None
    result_data: dict
    created_at: datetime
