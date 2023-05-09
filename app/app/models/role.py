from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Role(Base):
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, index=True)
    
    users = relationship('User', back_populates='role')
    
    def __str__(self) -> str:
        return self.role_name