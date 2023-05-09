from fastapi import APIRouter

from app.api.v1.endpoints import login, users, audios, logs

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(audios.router, prefix="/utils", tags=["audios"])
api_router.include_router(logs.router, prefix="/videos", tags=["logs"])