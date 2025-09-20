from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.anamnesis import Anamnesis
from schemas.anamnesis import AnamnesisIn
from repositories.mixins.crud import CRUDRepositoryMixin


class AnamnesisRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(Anamnesis, db)

    async def get(self, id: int) -> Anamnesis:
        return await super().get(id)

    async def get_by_visit_id(self, visit_id: int) -> Anamnesis | None:
        result = await self._db.execute(
            select(Anamnesis).where(Anamnesis.visit_id == visit_id)
        )
        return result.scalars().first()

    async def upsert_for_visit(self, visit_id: int, data: AnamnesisIn) -> Anamnesis:
        existing = await self.get_by_visit_id(visit_id)
        payload = data.dict(exclude_none=True)
        if existing:
            existing.data = payload
            self._db.add(existing)
            await self._db.commit()
            await self._db.refresh(existing)
            return existing
        inst = Anamnesis(visit_id=visit_id, data=payload)
        self._db.add(inst)
        await self._db.commit()
        await self._db.refresh(inst)
        return inst
