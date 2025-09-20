from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.examination import Examination
from repositories.mixins.crud import CRUDRepositoryMixin


class ExaminationRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(Examination, db)

    async def get(self, id: int) -> Examination:
        return await super().get(id)

    async def get_by_code(self, code: str) -> Examination | None:
        result = await self._db.execute(
            select(Examination).where(Examination.code == code)
        )
        return result.scalars().first()

    async def get_or_create_by_code(
        self,
        code: str,
        name: str | None = None,
        modality: str = "other",
        description: str | None = None,
    ) -> Examination:
        inst = await self.get_by_code(code)
        if inst:
            return inst
        inst = Examination(
            code=code, name=name or code, modality=modality, description=description
        )
        self._db.add(inst)
        await self._db.commit()
        await self._db.refresh(inst)
        return inst
