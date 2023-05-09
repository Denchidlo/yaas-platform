from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenUser(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = ''


class TokenPayload(BaseModel):
    user: Optional[TokenUser] = None
