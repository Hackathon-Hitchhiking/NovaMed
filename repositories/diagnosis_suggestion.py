from typing import Optional, Sequence, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.diagnosis_suggestion import DiagnosisSuggestion
from repositories.mixins.crud import CRUDRepositoryMixin


class DiagnosisSuggestionRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(DiagnosisSuggestion, db)

    async def get(self, id: int) -> DiagnosisSuggestion:
        return await super().get(id)

    async def list_for_visit(self, visit_id: int) -> Sequence[DiagnosisSuggestion]:
        result = await self._db.execute(
            select(DiagnosisSuggestion).where(DiagnosisSuggestion.visit_id == visit_id)
        )
        return result.scalars().all()

    async def replace_for_visit(
        self, visit_id: int, items: Sequence[Tuple[int, float, Optional[str]]]
    ) -> Sequence[DiagnosisSuggestion]:
        await self._db.execute(
            delete(DiagnosisSuggestion).where(DiagnosisSuggestion.visit_id == visit_id)
        )
        created: list[DiagnosisSuggestion] = []
        for disease_id, probability, rationale in items:
            inst = DiagnosisSuggestion(
                visit_id=visit_id,
                disease_id=disease_id,
                probability=probability,
                rationale=rationale,
            )
            self._db.add(inst)
            created.append(inst)
        await self._db.commit()
        for inst in created:
            await self._db.refresh(inst)
        return created
