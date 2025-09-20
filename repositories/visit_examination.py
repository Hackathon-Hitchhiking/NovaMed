from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.visit_examination import VisitExamination
from repositories.mixins.crud import CRUDRepositoryMixin


class VisitExaminationRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(VisitExamination, db)

    async def get(self, id: int) -> VisitExamination:
        return await super().get(id)

    async def add_result(
        self,
        visit_id: int,
        examination_name: str,
        s3_path: str,
        result_text: Optional[str],
        result_data: dict,
    ) -> VisitExamination:
        inst = VisitExamination(
            visit_id=visit_id,
            examination_name=examination_name,
            s3_path=s3_path,
            result_text=result_text,
            result_data=result_data or {},
        )
        self._db.add(inst)
        await self._db.commit()
        await self._db.refresh(inst)
        return inst

    async def list_for_visit(self, visit_id: int) -> Sequence[VisitExamination]:
        result = await self._db.execute(
            select(VisitExamination).where(VisitExamination.visit_id == visit_id)
        )
        return result.scalars().all()

    async def get_latest_for_visit(self, visit_id: int) -> VisitExamination | None:
        result = await self._db.execute(
            select(VisitExamination)
            .where(VisitExamination.visit_id == visit_id)
            .order_by(VisitExamination.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
