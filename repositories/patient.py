from sqlalchemy.ext.asyncio import AsyncSession

from models.patient import Patient
from repositories.mixins.crud import CRUDRepositoryMixin


class PatientRepository(CRUDRepositoryMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(Patient, db)

    async def get(self, id: int) -> Patient:  # narrow type
        return await super().get(id)
