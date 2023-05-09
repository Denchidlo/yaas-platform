from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import Event


class CRUDRole(CRUDBase):
    async def get_by_name(self, db: AsyncSession, name: str) -> Event:
        result = await db.execute(select(Event).where(Event.event_name == name))
        return result.scalars().first()

event = CRUDRole(Event)