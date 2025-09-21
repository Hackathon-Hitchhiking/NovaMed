from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.anamnesis import AnamnesisRepository
from repositories.diagnosis_suggestion import DiagnosisSuggestionRepository
from repositories.disease import DiseaseRepository
from repositories.referral_suggestion import ReferralSuggestionRepository
from repositories.visit import VisitRepository
from repositories.visit_examination import VisitExaminationRepository
from repositories.patient import PatientRepository
from schemas.anamnesis import AnamnesisIn, AnamnesisUpsertOut
from schemas.examination import ExamUploadIn, ExamUploadOut, ExamResultOut
from schemas.prediction import (
    DiagnosisSuggestionOut,
    PredictionsOut,
    ReferralSuggestionOut,
)
from schemas.visit import VisitCreateIn, VisitCreateOut, VisitOut
from schemas.patient import PatientCreateIn, PatientOut
from services.ml import MLClient
from services.storage import MinioStorage, StorageClient
from models.visit import Visit
from models.patient import Patient


class ClinicalDecisionService:
    def __init__(
        self,
        db: AsyncSession,
        ml_client: Optional[MLClient] = None,
        storage: Optional[StorageClient] = None,
    ) -> None:
        self.db = db
        self.storage = storage or MinioStorage()
        self.ml = ml_client or MLClient(storage=self.storage)

        # Repositories
        self.visit_repo = VisitRepository(db)
        self.anam_repo = AnamnesisRepository(db)
        self.dis_repo = DiseaseRepository(db)
        self.vexam_repo = VisitExaminationRepository(db)
        self.sugg_repo = DiagnosisSuggestionRepository(db)
        self.ref_repo = ReferralSuggestionRepository(db)
        self.patient_repo = PatientRepository(db)

    async def upload_anamnesis(
        self, visit_id: int, anamnesis: AnamnesisIn
    ) -> AnamnesisUpsertOut:
        logger.info(f"Upload anamnesis for visit={visit_id}")
        await self.visit_repo.get(visit_id)
        inst = await self.anam_repo.upsert_for_visit(visit_id, anamnesis)
        return AnamnesisUpsertOut(anamnesis_id=inst.id)

    async def upload_exam(self, visit_id: int, payload: ExamUploadIn) -> ExamUploadOut:
        logger.info(f"Upload exam for visit={visit_id} name={payload.examination_name}")
        await self.visit_repo.get(visit_id)
        # Upload bytes to storage to obtain an s3-style path
        s3_path = await self.storage.upload_bytes(
            data=payload.content,
            filename=payload.filename,
            content_type=payload.content_type,
        )
        vexam = await self.vexam_repo.add_result(
            visit_id=visit_id,
            examination_name=payload.examination_name,
            s3_path=s3_path,
            result_text=payload.result_text,
            result_data=(
                payload.result_data.model_dump() if payload.result_data else {}
            ),
        )
        return ExamUploadOut(s3_path=s3_path, visit_examination_id=vexam.id)

    async def get_anamnesis(self, visit_id: int) -> AnamnesisIn:
        logger.info(f"Get anamnesis for visit={visit_id}")
        await self.visit_repo.get(visit_id)
        anam = await self.anam_repo.get_by_visit_id(visit_id)
        return AnamnesisIn(**(anam.data if anam else {}))

    async def list_examinations(self, visit_id: int) -> list[ExamResultOut]:
        logger.info(f"List examinations for visit={visit_id}")
        await self.visit_repo.get(visit_id)
        items = await self.vexam_repo.list_for_visit(visit_id)
        return [
            ExamResultOut(
                id=i.id,
                examination_name=i.examination_name,
                s3_path=i.s3_path,
                result_text=i.result_text,
                result_data=i.result_data or {},
                created_at=i.created_at,
            )
            for i in items
        ]

    async def predict(self, visit_id: int) -> PredictionsOut:
        logger.info(f"Predict for visit={visit_id}")
        await self.visit_repo.get(visit_id)
        anam = await self.anam_repo.get_by_visit_id(visit_id)
        anam_data = AnamnesisIn(**anam.data) if anam else AnamnesisIn()
        latest_exam = await self.vexam_repo.get_latest_for_visit(visit_id)
        exam_path = latest_exam.s3_path if latest_exam else None

        dx_list, referrals = await self.ml.predict(
            anamnesis=anam_data, exam_path=exam_path
        )

        await self._persist_suggestions(
            visit_id, [(i.disease_name, i.probability, i.rationale) for i in dx_list]
        )
        await self._persist_referrals(visit_id, referrals)

        return PredictionsOut(
            suggestions=[
                DiagnosisSuggestionOut(
                    disease_name=i.disease_name,
                    probability=i.probability,
                    rationale=i.rationale,
                )
                for i in dx_list
            ],
            referrals=[ReferralSuggestionOut(specialty=s) for s in referrals],
        )

    async def _persist_suggestions(
        self, visit_id: int, dx_list: List[Tuple[str, float, Optional[str]]]
    ) -> Sequence:
        mapped: List[Tuple[int, float, Optional[str]]] = []
        for disease_name, prob, rationale in dx_list:
            disease = await self.dis_repo.get_or_create_by_name(disease_name)
            mapped.append((disease.id, prob, rationale))
        return await self.sugg_repo.replace_for_visit(visit_id, mapped)

    async def _persist_referrals(
        self, visit_id: int, specialties: List[str]
    ) -> Sequence:
        items = [(s, None) for s in specialties]
        return await self.ref_repo.replace_for_visit(visit_id, items)

    async def create_visit(self, payload: VisitCreateIn) -> VisitCreateOut:
        logger.info(f"Create visit for patient={payload.patient_id}")
        # Ensure patient exists (raises 404 if not)
        await self.patient_repo.get(payload.patient_id)

        visit = Visit(patient_id=payload.patient_id, doctor_id=payload.doctor_id)
        created = await self.visit_repo.create(visit)
        return VisitCreateOut(visit_id=created.id)

    async def get_visit(self, visit_id: int) -> VisitOut:
        v = await self.visit_repo.get(visit_id)
        return VisitOut(
            id=v.id,
            patient_id=v.patient_id,
            doctor_id=v.doctor_id,
            status=v.status,
            created_at=v.created_at,
        )

    async def list_visits(
        self, limit: int, offset: int, patient_id: Optional[int] = None
    ) -> list[VisitOut]:
        filters = {}
        if patient_id is not None:
            filters["patient_id"] = patient_id
        items = await self.visit_repo.list(limit=limit, offset=offset, **filters)
        return [
            VisitOut(
                id=i.id,
                patient_id=i.patient_id,
                doctor_id=i.doctor_id,
                status=i.status,
                created_at=i.created_at,
            )
            for i in items
        ]

    async def create_patient(self, payload: PatientCreateIn) -> PatientOut:
        p = Patient(
            date_of_birth=payload.date_of_birth,
            recorded_age=payload.recorded_age,
            sex=(payload.sex.value if payload.sex is not None else None),
        )
        created = await self.patient_repo.create(p)
        return PatientOut(
            id=created.id,
            date_of_birth=created.date_of_birth,
            recorded_age=created.recorded_age,
            sex=(created.sex if created.sex is not None else None),
            created_at=created.created_at,
        )

    async def get_patient(self, patient_id: int) -> PatientOut:
        p = await self.patient_repo.get(patient_id)
        return PatientOut(
            id=p.id,
            date_of_birth=p.date_of_birth,
            recorded_age=p.recorded_age,
            sex=(p.sex if p.sex is not None else None),
            created_at=p.created_at,
        )
