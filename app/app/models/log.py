from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, CheckConstraint, Text
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .event import Event  # noqa: F401


class Log(Base):
    id = Column(Integer, primary_key=True, index=True)
    event_dt = Column(DateTime, default=datetime.utcnow)
    log_payload = Column(String, default=True)

    event_id = Column(Integer, ForeignKey('event.id', ondelete='SET NULL'), nullable=True)
    
    event = relationship('Event', back_populates='logs')

    def __str__(self) -> str:
        return f"{self.event_id} - {self.created_at} - {self.payload}"
