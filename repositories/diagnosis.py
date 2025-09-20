from sqlalchemy.ext.asyncio import AsyncSession

from models.diagnosis import Diagnosis
from repositories.mixins.crud import CRUDRepositoryMixin


class DiagnosisRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(Diagnosis, db)

    async def get(self, id: int) -> Diagnosis:
        return await super().get(id)

    async def create_for_visit(
        self, visit_id: int, disease_id: int, confidence: float | None, note: str | None
    ) -> Diagnosis:
        inst = Diagnosis(
            visit_id=visit_id,
            disease_id=disease_id,
            confidence=confidence,
            is_final=True,
            note=note,
        )
        self._db.add(inst)
        await self._db.commit()
        await self._db.refresh(inst)
        return inst
