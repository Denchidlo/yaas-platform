from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, CheckConstraint, Text
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base

if TYPE_CHECKING:
    from .role import Role  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    connected_account_id = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean(), default=True)

    role_id = Column(Integer, ForeignKey('role.id', ondelete='SET NULL'), nullable=True)
    
    role = relationship('Role', back_populates='users')

    def __str__(self) -> str:
        return self.connected_account_id