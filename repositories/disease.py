from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.disease import Disease
from repositories.mixins.crud import CRUDRepositoryMixin


class DiseaseRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(Disease, db)

    async def get(self, id: int) -> Disease:
        return await super().get(id)

    async def get_or_create_by_name(
        self, name: str, specialty: str | None = None
    ) -> Disease:
        result = await self._db.execute(select(Disease).where(Disease.name == name))
        inst = result.scalars().first()
        if inst:
            return inst
        inst = Disease(name=name, specialty=specialty)
        self._db.add(inst)
        await self._db.commit()
        await self._db.refresh(inst)
        return inst
