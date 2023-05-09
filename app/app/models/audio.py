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
    SmallInteger
)
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .fingerprint import Fingerprint # noqa: F401


class Audio(Base):
    id = Column(Integer, primary_key=True, index=False, unique=True)
    filename = Column(String, nullable=False)
    fingerprinted = Column(SmallInteger, default=0)
    file_sha1 = Column(BYTEA, index=True)
    total_hashes = Column(Integer, nullable=False, default=0)
    dt_created = Column(DateTime, default=datetime.utcnow)
    dt_modified = Column(DateTime, default=datetime.utcnow)

    fingerprints = relationship('Fingerprint', back_populates='audio')

    def __str__(self) -> str:
        return self.filename
