from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models import Audio
from app.schemas.Audio import AudioCreate, AudioUpdate


class CRUDAudio(CRUDBase[Audio, AudioCreate, AudioUpdate]):
    
    async def get(self, db: AsyncSession, id: int) -> Audio:
        result = await db.execute(
            select(Audio)
            .where(and_(self.model.id == id)))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 10) -> List[Audio]:
        result = await db.execute(
            select(Audio)
            .order_by(Audio.dt_modified)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: AudioCreate) -> Audio:
        obj_in_data = jsonable_encoder(obj_in, exclude_none=True)
        db_obj = Audio(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_key(self, db: AsyncSession, key: str) -> Audio:
        result = await db.execute(
            select(Audio).where(Audio.filename == key)
        )
        return result.scalars().first()

audio = CRUDAudio(Audio)