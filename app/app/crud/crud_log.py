from typing import Any, Dict, Optional, Union, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models import Log, Event
from app.schemas.log import LogCreate, LogUpdate
from app.enums import VideoStatus


class CRUDLog(CRUDBase[Log]):
    async def get(self, db: AsyncSession, id: Any) -> Log:
        result = await db.execute(
            select(self.model)
            .options(joinedload(Log.event))
            .where(self.model.id == id)
        )
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 10) -> List[Log]:
        result = await db.execute(
            select(Log)
            .options(joinedload(Log.event))
            .order_by(Log.event_dt)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_multi_by_type(self, db: AsyncSession, *, skip: int = 0, limit: int = 10, type="RecognitionRequest") -> List[Log]:
        rec_event = await db.execute(
            select(Event)
            .where(
                Event.event_name == type
            )
        )
        rec_event_id = rec_event.scalars().first().id
        
        if not rec_event:
            raise AttributeError()(f"Unrecognized log type: {type}")

        result = await db.execute(
            select(Log)
            .where(Log.event_id == rec_event_id)
            .order_by(Log.dt_modified)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


log = CRUDLog(Log)