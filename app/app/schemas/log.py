from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr


# Shared properties
class LogBase(BaseModel):
    event_dt: Optional[datetime] = None
    event_id: Optional[int] = None
    log_payload: str = None


class LogInDBBase(LogBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class Log(LogInDBBase):
    pass

# Properties to receive via API on creation
class LogCreate(LogBase):
    log_payload: str

# Properties to receive via API on update
class LogUpdate(LogBase):
    log_payload: str
