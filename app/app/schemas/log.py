from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr


# Shared properties
class LogBase(BaseModel):
    event_dt: Optional[datetime] = None
    event_id: Optional[int] = None
    log_payload: str = None


class LogInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class Log(LogInDBBase):
    pass
