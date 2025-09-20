from sqlalchemy.ext.asyncio import AsyncSession

from models.visit import Visit
from repositories.mixins.crud import CRUDRepositoryMixin


class VisitRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(Visit, db)

    async def get(self, id: int) -> Visit:
        return await super().get(id)
