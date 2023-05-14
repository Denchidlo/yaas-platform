from typing import Optional
from datetime import datetime

from pydantic import BaseModel

# Shared properties
class AudioBase(BaseModel):
    filename: Optional[str] = None
    fingerprinted: Optional[int] = None
    dt_created: Optional[datetime] = None
    dt_modified: Optional[datetime] = None


# Properties to receive on Audio creation
class AudioCreate(AudioBase):
    fingerprinted: bool = False
    filename: str
    dt_created = datetime.now()
    dt_modified = datetime.now()


# Properties to receive on Audio update
class AudioUpdate(AudioBase):
    pass


# Properties shared by models stored in DB
class AudioInDBBase(AudioBase):
    id: int
    filename: str
    fingerprinted: int = 0
    dt_created: datetime
    dt_modified: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class Audio(AudioInDBBase):
    pass


# Properties properties stored in DB
class AudioInDB(AudioInDBBase):
    pass