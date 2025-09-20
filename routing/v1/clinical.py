from __future__ import annotations

import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from configs.Database import get_db_connection
from schemas.anamnesis import AnamnesisIn, AnamnesisUpsertOut
from schemas.examination import (
    ExamResultData,
    ExamUploadIn,
    ExamUploadOut,
    ExamResultOut,
)
from schemas.prediction import PredictionsOut
from schemas.visit import VisitCreateIn, VisitCreateOut, VisitOut
from schemas.patient import PatientCreateIn, PatientOut
from services.clinical import ClinicalDecisionService


router = APIRouter(prefix="/v1/clinical", tags=["clinical"])


@router.post("/patients", response_model=PatientOut)
async def create_patient(
    payload: PatientCreateIn,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.create_patient(payload)


@router.get("/patients/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.get_patient(patient_id)


@router.post("/visits", response_model=VisitCreateOut)
async def create_visit(
    payload: VisitCreateIn,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.create_visit(payload)


@router.get("/visits", response_model=List[VisitOut])
async def list_visits(
    limit: int = 50,
    offset: int = 0,
    patient_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.list_visits(limit=limit, offset=offset, patient_id=patient_id)


@router.get("/visits/{visit_id}", response_model=VisitOut)
async def get_visit(
    visit_id: int,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.get_visit(visit_id)


@router.post("/visits/{visit_id}/anamnesis", response_model=AnamnesisUpsertOut)
async def upload_anamnesis(
    visit_id: int,
    payload: AnamnesisIn,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.upload_anamnesis(visit_id, payload)


@router.post("/visits/{visit_id}/examinations", response_model=ExamUploadOut)
async def upload_exam(
    visit_id: int,
    examination_name: str = Form(...),
    file: UploadFile = File(...),
    result_text: Optional[str] = Form(None),
    result_data: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db_connection),
):
    extra_data = None
    if result_data:
        try:
            extra_data = ExamResultData(**json.loads(result_data))
        except Exception:
            extra_data = None

    content = await file.read()
    payload = ExamUploadIn(
        examination_name=examination_name,
        content=content,
        filename=file.filename,
        content_type=file.content_type,
        result_text=result_text,
        result_data=extra_data,
    )
    svc = ClinicalDecisionService(db)
    return await svc.upload_exam(visit_id, payload)


@router.post("/visits/{visit_id}/predict", response_model=PredictionsOut)
async def predict(
    visit_id: int,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.predict(visit_id)


@router.get("/visits/{visit_id}/anamnesis", response_model=AnamnesisIn)
async def get_anamnesis(
    visit_id: int,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.get_anamnesis(visit_id)


@router.get("/visits/{visit_id}/examinations", response_model=List[ExamResultOut])
async def list_examinations(
    visit_id: int,
    db: AsyncSession = Depends(get_db_connection),
):
    svc = ClinicalDecisionService(db)
    return await svc.list_examinations(visit_id)
