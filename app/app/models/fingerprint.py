from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, 
    Column, 
    DateTime, 
    ForeignKey, 
    Integer, 
    String, 
    Table, 
    CheckConstraint, 
    Text, 
    BigInteger,
    Sequence
)
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .audio import Audio # noqa: F401


class Fingerprint(Base):
    id = Column(Integer, 
        Sequence('fingerprint_id_seq', start=1, increment=1, schema='public'), 
        primary_key=True
    )
    hash = Column(BigInteger, nullable=False, index=True)
    audio_id = Column(Integer, ForeignKey('audio.id', ondelete='CASCADE'), nullable=False)
    offset = Column(Integer, nullable=False)

    audio = relationship('Audio', back_populates='fingerprints')

    def __str__(self) -> str:
        return f'{self.audio_id} - {self.hash} - {self.offset}'
