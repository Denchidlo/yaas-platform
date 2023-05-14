from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


# Shared properties
class RoleBase(BaseModel):
    role_name: str = None


class RoleInDBBase(RoleBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class Role(RoleInDBBase):
    pass

# Properties to receive via API on creation
class RoleCreate(RoleBase):
    role_name: str

# Properties to receive via API on update
class RoleUpdate(RoleBase):
    role_name: str
