from typing import Optional, Sequence, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.referral_suggestion import ReferralSuggestion
from repositories.mixins.crud import CRUDRepositoryMixin


class ReferralSuggestionRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(ReferralSuggestion, db)

    async def get(self, id: int) -> ReferralSuggestion:
        return await super().get(id)

    async def list_for_visit(self, visit_id: int) -> Sequence[ReferralSuggestion]:
        result = await self._db.execute(
            select(ReferralSuggestion).where(ReferralSuggestion.visit_id == visit_id)
        )
        return result.scalars().all()

    async def replace_for_visit(
        self, visit_id: int, items: Sequence[Tuple[str, Optional[str]]]
    ) -> Sequence[ReferralSuggestion]:
        await self._db.execute(
            delete(ReferralSuggestion).where(ReferralSuggestion.visit_id == visit_id)
        )
        created: list[ReferralSuggestion] = []
        for specialty, note in items:
            inst = ReferralSuggestion(visit_id=visit_id, specialty=specialty, note=note)
            self._db.add(inst)
            created.append(inst)
        await self._db.commit()
        for inst in created:
            await self._db.refresh(inst)
        return created
