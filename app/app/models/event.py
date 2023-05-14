from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .log import Log  # noqa: F401


class Event(Base):
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, index=True)
    
    logs = relationship('Log', back_populates='event')
    
    def __str__(self) -> str:
        return self.event_name