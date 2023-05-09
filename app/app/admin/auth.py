from typing import Optional
from datetime import timedelta

from fastapi import HTTPException, status
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from pydantic import ValidationError
from jose import jwt

from app import crud, schemas
from app.db.session import async_session_factory
from app.core import security
from app.core.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        async with async_session_factory() as db:
            user = await crud.user.authenticate(
                db, email=form['username'], password=form['password']
            )
            if not user:
                raise HTTPException(status_code=400, detail="Incorrect email or password")
            elif not crud.user.is_active(user):
                raise HTTPException(status_code=400, detail="Inactive user")
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            token = security.create_access_token(
                    user, expires_delta=access_token_expires
                )
            request.session.update({"token": token})

            return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get("token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = schemas.TokenPayload(**payload)
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        async with async_session_factory() as db:
            user = await crud.user.get(db, id=token_data.user.id)
            if not user:
                raise HTTPException(status_code=404, detail="No user found")
            if not crud.user.is_active(user):
                raise HTTPException(status_code=400, detail="Inactive user")
            if not crud.user.is_superuser(user):
                raise HTTPException(status_code=400, detail="Insufficent permissions")
            return True